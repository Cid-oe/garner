"""Builds a candidate source + test suite in an isolated copy of the sample project and runs it."""

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .bob import ROOT

SAMPLE = ROOT / "sample"
SOURCE_REL = Path("src/main/java/com/acme/billing/InvoiceCalculator.java")
TEST_DIR_REL = Path("src/test/java/com/acme/billing")


@dataclass
class TestRun:
    label: str
    compiled: bool
    tests: int = 0
    failures: int = 0
    errors: int = 0
    failed: list = field(default_factory=list)  # [{"name", "message"}]
    log_tail: str = ""

    @property
    def passed(self) -> bool:
        return self.compiled and self.tests > 0 and self.failures == 0 and self.errors == 0


def extract_java(response: str, must_contain: str) -> str:
    """Returns the largest ```java block containing `must_contain`, or the raw text if it is plain Java."""
    blocks = re.findall(r"```(?:java)?\s*\n(.*?)```", response, flags=re.S)
    candidates = [b for b in blocks if must_contain in b]
    if candidates:
        return max(candidates, key=len).strip() + "\n"
    if must_contain in response and "package " in response:
        return response.strip() + "\n"
    raise ValueError(f"no Java code containing '{must_contain}' in Bob's response")


def class_name(java: str) -> str:
    m = re.search(r"\bclass\s+(\w+)", java)
    if not m:
        raise ValueError("no class declaration found")
    return m.group(1)


def run_suite(workdir: Path, source: str, tests: dict, label: str, timeout: int = 300) -> TestRun:
    """Copies the sample project to `workdir`, installs `source` and `tests` ({ClassName: code}), runs mvn test."""
    if workdir.exists():
        shutil.rmtree(workdir)
    shutil.copytree(SAMPLE, workdir, ignore=shutil.ignore_patterns("target"))
    test_dir = workdir / TEST_DIR_REL
    shutil.rmtree(test_dir, ignore_errors=True)
    test_dir.mkdir(parents=True)
    (workdir / SOURCE_REL).write_text(source, encoding="utf-8")
    for name, code in tests.items():
        (test_dir / f"{name}.java").write_text(code, encoding="utf-8")

    proc = subprocess.run(
        ["mvn", "-q", "-B", "test", "-Dsurefire.failIfNoSpecifiedTests=false"],
        cwd=workdir, capture_output=True, text=True, timeout=timeout,
    )
    log = (proc.stdout + proc.stderr)
    log = "\n".join(l for l in log.splitlines() if not l.startswith("Picked up JAVA_TOOL_OPTIONS"))
    reports = sorted((workdir / "target" / "surefire-reports").glob("TEST-*.xml"))
    if not reports:
        return TestRun(label, compiled=False, log_tail=log[-3000:])

    run = TestRun(label, compiled=True, log_tail=log[-3000:])
    for rep in reports:
        root = ET.parse(rep).getroot()
        run.tests += int(root.get("tests", 0))
        run.failures += int(root.get("failures", 0))
        run.errors += int(root.get("errors", 0))
        for case in root.iter("testcase"):
            bad = case.find("failure")
            if bad is None:
                bad = case.find("error")
            if bad is not None:
                msg = (bad.get("message") or bad.text or "").strip().splitlines()
                run.failed.append({"name": f"{case.get('classname', '').split('.')[-1]}.{case.get('name')}",
                                   "message": msg[0][:300] if msg else ""})
    return run


def apply_mutant(source: str, mutant: dict) -> str:
    out = source
    for old, new in mutant["replacements"]:
        if old not in out:
            raise ValueError(f"mutant {mutant['id']}: '{old}' not found in source")
        out = out.replace(old, new)
    return out
