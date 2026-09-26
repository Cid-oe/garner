"""The Legacy Bridge pipeline: characterize -> modernize -> verify -> report."""

import difflib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import bob, prompts
from .javaproj import SAMPLE, SOURCE_REL, TEST_DIR_REL, apply_mutant, class_name, extract_java, run_suite

ROOT = bob.ROOT
RUNS = ROOT / "runs"
OUT = ROOT / "out"
MUTANTS = json.loads((ROOT / "harness" / "mutants.json").read_text(encoding="utf-8"))
TEST_CLASS = "InvoiceCalculatorCharacterizationTest"


def _log(msg):
    print(f"[bridge] {msg}", flush=True)


class Run:
    """One pipeline run; everything it produces lives in runs/<id>/ and state.json."""

    def __init__(self, run_id=None):
        self.id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.dir = RUNS / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        state_file = self.dir / "state.json"
        self.state = json.loads(state_file.read_text()) if state_file.exists() else {
            "id": self.id, "source_file": str(SOURCE_REL), "modes": [], "characterization": None, "modernizations": []}

    @classmethod
    def latest(cls):
        runs = sorted(p.name for p in RUNS.glob("*") if (p / "state.json").exists())
        if not runs:
            raise SystemExit("no runs yet; run `bob-bridge generate-tests` first")
        return cls(runs[-1])

    def save(self):
        (self.dir / "state.json").write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        (RUNS / "LATEST").write_text(self.id, encoding="utf-8")

    def _note_mode(self, ex):
        if ex.mode not in self.state["modes"]:
            self.state["modes"].append(ex.mode)
        self.state["bob_calls"] = self.state.get("bob_calls", 0) + 1
        if ex.cost is not None:
            self.state["bob_cost"] = round(self.state.get("bob_cost", 0) + ex.cost, 3)


def original_source():
    return (SAMPLE / SOURCE_REL).read_text(encoding="utf-8")


def control_tests():
    return {"ControlQuirksTest": (SAMPLE / TEST_DIR_REL / "ControlQuirksTest.java").read_text(encoding="utf-8")}


def mutation_score(run: Run, suite: dict, label: str):
    """Runs `suite` against each single-quirk mutant of the original. Killed = at least one test fails."""
    src = original_source()

    def one(m):
        r = run_suite(run.dir / "mutants" / label / m["id"], apply_mutant(src, m), suite, m["id"])
        return {"id": m["id"], "quirk": m["quirk"], "killed": not r.passed,
                "by": [f["name"] for f in r.failed][:3], "compiled": r.compiled}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, MUTANTS))
    return {"killed": sum(r["killed"] for r in results), "total": len(results), "mutants": results}


def generate_tests(run: Run, mode=None, max_fix_rounds=1, max_harden_rounds=1):
    """R1: Bob writes a characterization suite that passes on the unmodified legacy file."""
    src = original_source()
    _log("asking Bob for characterization tests")
    ex = bob.ask("generate-tests", prompts.GENERATE_TESTS.format(test_class=TEST_CLASS, source=src), mode)
    run._note_mode(ex)
    exchanges = [ex.transcript]
    tests = extract_java(ex.response, "class ")
    name = class_name(tests)

    baseline = run_suite(run.dir / "baseline", src, {name: tests}, "original")
    rounds = 0
    while not baseline.passed and rounds < max_fix_rounds:
        rounds += 1
        _log(f"{baseline.failures + baseline.errors} test(s) fail on the original; asking Bob to fix them")
        failures = "\n".join(f"- {f['name']}: {f['message']}" for f in baseline.failed) or baseline.log_tail[-1500:]
        ex = bob.ask("fix-tests", prompts.FIX_TESTS.format(test_class=name, failures=failures, tests=tests, source=src), mode)
        run._note_mode(ex)
        exchanges.append(ex.transcript)
        tests = extract_java(ex.response, "class ")
        name = class_name(tests)
        baseline = run_suite(run.dir / "baseline", src, {name: tests}, "original")

    (run.dir / f"{name}.java").write_text(tests, encoding="utf-8")
    _log(f"baseline: {baseline.tests} tests, {'all pass' if baseline.passed else 'FAILING'} on the original")

    _log("scoring the suite against behaviour mutants")
    bob_score = mutation_score(run, {name: tests}, "bob") if baseline.passed else None
    first_score = bob_score
    harden_rounds = 0
    while bob_score and bob_score["killed"] < bob_score["total"] and harden_rounds < max_harden_rounds:
        harden_rounds += 1
        survivors = [m for m in MUTANTS if not next(r for r in bob_score["mutants"] if r["id"] == m["id"])["killed"]]
        _log(f"{len(survivors)} mutant(s) survived; asking Bob to harden its suite")
        described = "\n".join(f"- {m['id']}: " + "; ".join(f"`{a}` became `{b}`" for a, b in m["replacements"]) for m in survivors)
        ex = bob.ask("harden-tests", prompts.HARDEN.format(test_class=name, survivors=described, tests=tests, source=src), mode)
        run._note_mode(ex)
        exchanges.append(ex.transcript)
        hardened = extract_java(ex.response, "class ")
        check = run_suite(run.dir / "baseline-hardened", src, {class_name(hardened): hardened}, "original")
        if not check.passed:
            _log("hardened suite fails on the original; keeping the previous suite")
            break
        tests, name, baseline = hardened, class_name(hardened), check
        (run.dir / f"{name}.java").write_text(tests, encoding="utf-8")
        bob_score = mutation_score(run, {name: tests}, f"bob-h{harden_rounds}")
    control_score = mutation_score(run, control_tests(), "control")

    run.state["characterization"] = {
        "test_class": name,
        "test_file": str((run.dir / f"{name}.java").relative_to(ROOT)),
        "baseline": asdict(baseline),
        "fix_rounds": rounds,
        "mutation": bob_score,
        "mutation_before_hardening": first_score if harden_rounds else None,
        "harden_rounds": harden_rounds,
        "control_mutation": control_score,
        "transcripts": exchanges,
    }
    run.save()
    return run.state["characterization"]


def modernize(run: Run, goal: str, step: str = "modernize", mode=None, apply=True, repair=True):
    """R2/R3: Bob modernizes the file; the change is applied only if the characterization suite still passes."""
    char = run.state.get("characterization")
    if not char or not char["baseline"]["compiled"] or char["baseline"]["failures"] or char["baseline"]["errors"]:
        raise SystemExit("no passing characterization suite in this run; run generate-tests first")
    src = original_source()
    tests = {char["test_class"]: (ROOT / char["test_file"]).read_text(encoding="utf-8")}

    _log(f"asking Bob to modernize: {goal}")
    ex = bob.ask(step, prompts.MODERNIZE.format(goal=goal, source=src), mode)
    run._note_mode(ex)
    try:
        candidate = extract_java(ex.response, "class InvoiceCalculator")
    except ValueError as e:
        record = {"step": step, "goal": goal, "verdict": "NOT ATTEMPTED", "reason": str(e), "transcript": ex.transcript}
        run.state["modernizations"].append(record)
        run.save()
        return record

    attempt_dir = run.dir / step
    attempt_dir.mkdir(exist_ok=True)
    (attempt_dir / "InvoiceCalculator.java").write_text(candidate, encoding="utf-8")

    _log("re-running the characterization suite against Bob's version")
    result = run_suite(attempt_dir / "work", candidate, tests, "candidate")
    control = run_suite(attempt_dir / "control", candidate, control_tests(), "control")
    verdict = "VERIFIED" if result.passed else "BLOCKED"

    applied_to = None
    if verdict == "VERIFIED" and apply:
        OUT.mkdir(exist_ok=True)
        (OUT / "InvoiceCalculator.java").write_text(candidate, encoding="utf-8")
        applied_to = str((OUT / "InvoiceCalculator.java").relative_to(ROOT))
    _log(f"verdict: {verdict}" + (f" -> applied to {applied_to}" if applied_to else " -> not applied"))

    diff = "".join(difflib.unified_diff(src.splitlines(True), candidate.splitlines(True),
                                        "legacy/InvoiceCalculator.java", "bob/InvoiceCalculator.java"))
    record = {
        "step": step, "goal": goal, "verdict": verdict, "applied_to": applied_to,
        "result": asdict(result), "control": asdict(control), "diff": diff,
        "transcript": ex.transcript,
    }

    if verdict == "BLOCKED" and repair:
        _log("blocked; sending the failing tests back to Bob to repair")
        failures = "\n".join(f"- {f['name']}: {f['message']}" for f in result.failed) or result.log_tail[-1500:]
        rex = bob.ask(f"{step}-repair", prompts.REPAIR.format(failures=failures, candidate=candidate, source=src), mode)
        run._note_mode(rex)
        try:
            fixed = extract_java(rex.response, "class InvoiceCalculator")
        except ValueError as e:
            record["repair"] = {"verdict": "NOT ATTEMPTED", "reason": str(e), "transcript": rex.transcript}
        else:
            (attempt_dir / "InvoiceCalculator.repaired.java").write_text(fixed, encoding="utf-8")
            again = run_suite(attempt_dir / "work-repaired", fixed, tests, "repaired")
            r_verdict = "VERIFIED" if again.passed else "BLOCKED"
            r_applied = None
            if r_verdict == "VERIFIED" and apply:
                OUT.mkdir(exist_ok=True)
                (OUT / "InvoiceCalculator.java").write_text(fixed, encoding="utf-8")
                r_applied = str((OUT / "InvoiceCalculator.java").relative_to(ROOT))
            record["repair"] = {
                "verdict": r_verdict, "applied_to": r_applied, "result": asdict(again),
                "diff": "".join(difflib.unified_diff(candidate.splitlines(True), fixed.splitlines(True),
                                                     "bob/blocked.java", "bob/repaired.java")),
                "transcript": rex.transcript,
            }
            _log(f"repair verdict: {r_verdict}" + (f" -> applied to {r_applied}" if r_applied else ""))
    run.state["modernizations"].append(record)
    run.save()
    return record
