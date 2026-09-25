# Legacy Bridge

**IBM Bob modernizes legacy Java. Bob's own characterization tests decide what ships.**

Modernizing legacy code is risky because nobody knows everything the old code does. Legacy Bridge
has Bob pin down today's behaviour in a characterization-test suite first, then lets Bob modernize.
A change ships only if every characterization test still passes. When a "cleanup" silently changes
behaviour, the suite catches it and the change is blocked, with the exact difference in the report.

Bob also closes both loops itself: if its tests miss a behaviour mutant, Bob sees what slipped
through and hardens the suite; if a modernization is blocked, Bob gets the failing tests and
repairs its own code until the suite passes.

```
legacy file ──> Bob writes characterization tests ──> pass on the legacy code? ──> scored against behaviour mutants
                                                                      │
Bob modernizes ──> re-run the suite ──> all pass: VERIFIED, applied   │
                                   └──> any fail: BLOCKED, not applied, diff + failing tests in the report
```

## Quick start

Requires Java 21, Maven, Python 3.11.

```bash
export BOB_CMD='<Bob non-interactive command>'   # see "Connecting Bob"
./bob-bridge demo                                 # tests -> benign modernization -> risky modernization -> report
open runs/$(cat runs/LATEST)/report.html
```

Step by step:

```bash
./bob-bridge generate-tests                              # R1: Bob writes the characterization suite
./bob-bridge modernize --goal "..." --step my-attempt    # R2/R3: verified -> out/, blocked -> not applied
./bob-bridge report                                      # R4: standalone HTML report
streamlit run app.py                                     # R5: one-click demo page
```

## How Bob is used

Every reasoning step is a real Bob call, and every call is saved to `bob_sessions/` (prompt, response,
command, duration): writing the characterization suite, fixing any test that fails on the original
code, and each modernization. The harness only builds, runs tests, and reports.

| Mode | What it does | When |
|---|---|---|
| `cli` (default) | Runs `$BOB_CMD`; prompt on stdin, or in a file if the command contains `{prompt_file}` | Real runs |
| `replay` | Replays the latest recorded Bob session for each step | Hosted demo, no API key needed; the report says it is a replay |
| `fixture` | Hand-written responses in `harness/fixtures/` | Developing the harness offline. **Not Bob.** The report shows a banner and these transcripts are never committed |

### Connecting Bob

Set `BOB_CMD` to the command that sends a prompt to Bob and prints its reply, for example Bob Shell in
non-interactive mode. Check it with a one-line prompt first:

```bash
echo "Reply with the word ready" | $BOB_CMD
```

## The sample

`sample/` is a fabricated 2004-era invoice calculator with four real quirks, each a trap for a
plausible-looking modernization. See [sample/QUIRKS.md](sample/QUIRKS.md).

The harness scores Bob's suite by **mutation**: it breaks each quirk in isolation
(`harness/mutants.json`) and checks that Bob's tests catch it. The hand-written
`ControlQuirksTest` is the reference; it catches 4/4.

## Layout

```
sample/            legacy Maven project (the code under modernization) + control tests
harness/bridge/    pipeline: Bob client, test runner, mutation scoring, report, CLI
harness/fixtures/  offline fixtures (not Bob)
bob_sessions/      recorded Bob sessions (evidence)
app.py             Streamlit demo page
runs/<id>/         per-run workspaces, state.json, report.html (not committed)
out/               last verified modernization (not committed)
```
