"""Talking to IBM Bob, with every exchange recorded to bob_sessions/.

Modes:
  cli      Runs the command in $BOB_CMD (e.g. Bob Shell in non-interactive mode).
           The prompt goes to stdin, or into a temp file if the command
           contains {prompt_file}. Stdout is the response.
  replay   Returns the response from a previously recorded Bob session with the
           same step name. Used by the hosted demo so judges can click through
           without an API key; the report says it is a replay.
  fixture  Canned, hand-written responses for developing the harness offline.
           NOT Bob. The report shows a banner and transcripts are marked.
"""

import json
import os
import re
import shutil
import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = ROOT / "bob_sessions"
FIXTURES = ROOT / "harness" / "fixtures"


class BobError(RuntimeError):
    pass


@dataclass
class Exchange:
    step: str
    mode: str
    prompt: str
    response: str
    command: str
    started_at: str
    seconds: float
    transcript: str = ""


def _now():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _record(ex: Exchange) -> Exchange:
    SESSIONS.mkdir(exist_ok=True)
    name = f"{ex.started_at}-{ex.step}-{ex.mode}"
    path = SESSIONS / f"{name}.md"
    banner = "" if ex.mode == "cli" else f"> Mode: **{ex.mode}**. " + (
        "Replayed from an earlier recorded Bob session.\n\n" if ex.mode == "replay"
        else "Hand-written fixture for offline development. This is NOT Bob output.\n\n")
    path.write_text(
        f"# Bob session: {ex.step}\n\n{banner}"
        f"- Started: {ex.started_at}\n- Command: `{ex.command}`\n- Duration: {ex.seconds:.1f}s\n\n"
        f"## Prompt\n\n````\n{ex.prompt}\n````\n\n## Response\n\n````\n{ex.response}\n````\n",
        encoding="utf-8",
    )
    (SESSIONS / f"{name}.json").write_text(json.dumps(asdict(ex), indent=2), encoding="utf-8")
    ex.transcript = str(path.relative_to(ROOT))
    return ex


ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _run_cli(prompt: str, timeout: int) -> tuple[str, str]:
    """Runs $BOB_CMD. Placeholders: {prompt} (prompt as one argument, e.g. BOB_CMD='bob -p {prompt}'),
    {prompt_file} (path to a file holding the prompt). With neither, the prompt goes to stdin.
    Bob runs in an empty scratch directory so, as an agent, it cannot edit the repo."""
    template = os.environ.get("BOB_CMD")
    if not template:
        raise BobError("BOB_CMD is not set; e.g. export BOB_CMD='bob -p {prompt}' (see README)")
    workdir = tempfile.mkdtemp(prefix="bob-bridge-")
    prompt_file = os.path.join(workdir, "PROMPT.md")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    parts = shlex.split(template)
    stdin = None if any("{prompt" in p for p in parts) else prompt
    cmd = [p.replace("{prompt_file}", prompt_file) if "{prompt_file}" in p
           else (prompt if p == "{prompt}" else p) for p in parts]
    shown = " ".join("<prompt>" if c == prompt else c for c in cmd)
    try:
        proc = subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=timeout, cwd=workdir)
    except subprocess.TimeoutExpired as e:
        raise BobError(f"Bob timed out after {timeout}s") from e
    except FileNotFoundError as e:
        raise BobError(f"cannot run '{cmd[0]}': not found on PATH") from e
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if proc.returncode != 0:
        raise BobError(f"Bob exited {proc.returncode}: {(proc.stderr or proc.stdout).strip()[-800:]}")
    return ANSI.sub("", proc.stdout), shown


def _run_replay(step: str) -> tuple[str, str]:
    recorded = sorted(p for p in SESSIONS.glob(f"*-{step}-cli.json"))
    if not recorded:
        raise BobError(f"no recorded Bob session for step '{step}' to replay")
    data = json.loads(recorded[-1].read_text(encoding="utf-8"))
    return data["response"], f"replay of {recorded[-1].name}"


def _run_fixture(step: str) -> tuple[str, str]:
    path = FIXTURES / f"{step}.response.md"
    if not path.exists():
        raise BobError(f"no fixture response for step '{step}' at {path}")
    return path.read_text(encoding="utf-8"), f"fixture {path.name}"


def ask(step: str, prompt: str, mode: str | None = None, timeout: int = 600) -> Exchange:
    """Sends one prompt to Bob and records the exchange. `step` names it (e.g. 'generate-tests')."""
    mode = mode or os.environ.get("BRIDGE_MODE", "cli")
    started = _now()
    t0 = time.monotonic()
    if mode == "cli":
        response, command = _run_cli(prompt, timeout)
    elif mode == "replay":
        response, command = _run_replay(step)
    elif mode == "fixture":
        response, command = _run_fixture(step)
    else:
        raise BobError(f"unknown mode '{mode}' (cli, replay, fixture)")
    return _record(Exchange(step, mode, prompt, response, command, started, time.monotonic() - t0))
