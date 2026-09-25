# Garner: hackathon plan

IBM Bob 2.0 Hackathon (lablab.ai), online, 48h, Sept 25-27 2026. Prize pool about $10-12K.
Judged on presentation, business value, application of technology, originality (confirm on the live page).

## Pitch

Bob 2.0 added skills and subagents. Teams now collect thousands of them, and every installed skill's
description sits in Bob's context on every task. Our test library has 6,320 items: loading them all
costs about 320,000 tokens, so nobody can. **Garner reads the task and the repo, picks the 3-7 items
that matter, blocks the risky ones, and installs them into Bob.** About 250 tokens instead of 320,000.

## Judge review (honest, current state)

| Criterion | Score | Biggest weakness | Fix |
|---|---|---|---|
| Presentation | 4/10 | A CLI printing a table. Nothing to look at. | Split-screen before/after video; visual "loadout card" report |
| Business value | 6/10 | Only hurts people who already hoard skills | Frame as enterprise skill governance: policy, audit trail, allowlists |
| Application of technology | 5/10 | Bob is just the folder we write to | Garner runs *inside* Bob as a skill; Bob's subagents run the picked squad; Granite on watsonx.ai reranks |
| Originality | 7/10 | "Skill search" ideas will exist | Coverage-aware selection + governance + measured context savings |

**Placing now:** middle of the pack, top 20% at best. Not a 2nd-prize entry yet.
**With the fixes below:** a real shot at the top 10, and a podium chance if the demo lands.
Base rate matters: roughly 500 submissions, so no idea is "worth 2nd place" by itself. The demo decides.

### Highest-leverage change

**Point the demo at legacy modernization.** IBM's own Bob V2 launch leads with multi-agent
modernization workflows. Demo: a real COBOL program -> Garner assembles a squad (COBOL analyst,
Java architect, test writer) -> Bob runs them as subagents -> working Java plus tests. Same engine,
but now the judges see IBM's favourite use case done better, with a before/after they can read.

## Premortem

It is Sept 28. We were not shortlisted. Why?

| # | Cause | L | I | LxI | Prevention |
|---|---|---|---|---|---|
| 1 | Demo was a terminal table; judges skimmed past | 4 | 5 | 20 | Before/after split screen; HTML loadout card; lead with the 320K -> 250 number |
| 2 | Installing into `.bob/skills` didn't behave as the docs said | 3 | 5 | 15 | Test in real Bob in the first 2 hours of access; adapt the installer same day |
| 3 | Picks looked random on stage (keyword ranking) | 3 | 5 | 15 | Granite rerank on watsonx.ai; pre-test the exact demo tasks |
| 4 | Bob was not load-bearing: "this works with any agent" | 4 | 4 | 16 | Garner as a Bob skill invoked mid-task; Bob subagents execute the squad |
| 5 | No proof it helps: token savings only, no quality result | 4 | 3 | 12 | 3-task benchmark: bare Bob vs Garner Bob, tests pass/fail + tokens |
| 6 | Bob access or rate limits hit during the event | 3 | 4 | 12 | Record the demo by hour 30; keep a CLI-only fallback video |
| 7 | Judges couldn't reproduce: the library is private and community-sourced | 3 | 3 | 9 | Ship the indexer, not the content; demo on public skill libraries too |
| 8 | Submitted late or with broken links / private repo | 2 | 5 | 10 | Draft submission at hour 40; make the repo public; check every link logged out |

### Tripwires

- Hour 6: Garner-installed skills don't activate in Bob -> switch the installer to whatever format Bob actually loads, before any new feature.
- Hour 24: modernization demo not working end to end -> fall back to the "OAuth + tests" demo, keep modernization as a slide.
- Hour 30: no recorded demo -> stop building, record what works.
- Hour 40: not submitted -> submit the draft now, improve after.

## Scope

- **Must:** golden path works in real Bob; before/after video under the time limit; public repo with README; submission done by hour 44.
- **Should:** Granite rerank; Garner callable from inside Bob; 3-task benchmark; HTML loadout card.
- **Could:** watsonx Orchestrate flow; semantic embeddings index; a Bob plugin package.

## Golden path (demo)

```bash
garner index --lib ./ECC --lib ./skill-library   # ECC = curated core, second = long tail
garner pick "modernize PAYROLL.cbl to Java with tests" --repo ./payroll-demo
garner install "modernize PAYROLL.cbl to Java with tests" --repo ./payroll-demo --target bob
# In Bob: run the same task; the installed squad does the work
```

## ECC integration

[affaan-m/ECC](https://github.com/affaan-m/ECC) (MIT, v2.2.2) is a trending "agent harness OS": 292 skills,
68 agents, 94 commands, 122 rules, and an installer with adapters for about 15 tools (Claude, Cursor, Codex,
Kiro, Qwen, Zed, Antigravity...). **It has no IBM Bob support.** Its selective install already takes
`--skills a,b,c --target <tool>`, but the user has to know which skills to name.

**The combined story: ECC is the library and the installer; Garner is the brain that picks.**

```
task + repo --> Garner (rank + policy) --> ECC install plan (--skills ... --target bob) --> .bob/
```

### What we build

| # | Piece | Where | Size |
|---|---|---|---|
| 1 | `bob-project` install target (`.bob/skills`, `.bob/rules`) | fork of ECC | ~10 lines + registry + module targets |
| 2 | Garner indexes ECC as the default curated library | garner | done (works unchanged: 292 skills, 68 agents) |
| 3 | `garner install --via ecc`: hand the pick to ECC's `install-plan.js`/`install-apply.js` | garner | small |
| 4 | Granite rerank on watsonx.ai over the top 30 candidates | garner | medium |
| 5 | Upstream PR "Add IBM Bob target" to ECC | GitHub | small; a strong line for judges |

### Why this helps the scores

- **Application of technology**: ECC + Bob target means ECC's whole catalogue works in Bob, not just ours.
- **Business value**: rides an existing, popular project; a merged upstream PR is proof of adoption.
- **Reproducibility (premortem risk 7)**: judges can clone ECC; no private library needed. The 6,320-item
  library stays as the "long tail" to show scale (320K tokens).

### Progress

- **Bob target for ECC: done** on `Cid-oe/ECC` branch `feat/ibm-bob-target`. `install.sh --target bob`
  installs skills to `.bob/skills/`, flat rules to `.bob/rules/`, commands to `.bob/commands/`; agents
  are excluded. Adapter test added; the target-related test files pass. The full suite has 28 failures:
  most fail identically on untouched upstream, `control-pane` passes when run alone, and the two
  `harness-capabilities` failures (hard-coded tool counts) were fixed in the same commit.
  Upstream PR not opened yet.
- **Pitch evidence:** in ECC, `--skills tdd-workflow` installs **48 skills**, because the skill ships
  inside the `workflow-quality` module. Asking for one skill gets you 48. That is Garner's problem
  statement, measured on a popular project.

### Measured so far (keyword ranker on ECC)

- Works: "security review before release" picks `security-review` + `security-reviewer`.
- Misses: "profile it" pulls `linkedin-profile-optimizer`; "OAuth" pulls `x-api`. Word sense needs the
  Granite rerank (step 4). This moves the rerank from Should to **Must**.

### Premortem additions

| # | Cause | L | I | LxI | Prevention |
|---|---|---|---|---|---|
| 9 | ECC's installer is complex (441-line helpers, install state) and eats the day | 3 | 4 | 12 | Timebox ECC target to 2h; fall back to Garner's own installer, keep ECC as library only |
| 10 | Upstream PR not merged in 48h | 4 | 2 | 8 | Present it as "PR opened"; never depend on merge |
| 11 | ECC agents use Claude tool names that Bob ignores or rejects | 3 | 3 | 9 | Test one ECC agent in Bob in the first access hour |
| 12 | Demo drifts: two libraries, two installers, one pitch | 3 | 4 | 12 | One sentence pitch stays Garner; ECC appears as "works with ECC" |

### Demo decision

ECC has strong Java/Spring/security/TDD content but no COBOL. Two options:
- **A (recommended):** index ECC + the long-tail library together; modernization demo uses ECC's Java/TDD
  skills plus the long tail's `cobol-engineer` / `legacy-analyst`.
- **B:** switch the demo to "security review + tests before release" on ECC only. Simpler, less IBM-flavoured.

## Next 3 tasks

1. **Granite rerank** (2h): `--rerank watsonx` sends task + top 30 candidates to Granite, keeps the order it
   returns; falls back to keyword ranking when no API key. Done when the two misses above disappear.
2. ~~**Bob target for ECC**~~ done;: fork ECC, add `bob-project` target, `install-plan.js --target bob`
   dry-runs clean. Done when a Garner pick installs into `.bob/` through ECC.
3. **Demo repo** (2h): small COBOL payroll program + expected Java behaviour tests; run the golden path end
   to end in Bob the first hour Bob access works.

## Planning tools in this repo

- Skills (Bob and Claude Code): `.bob/skills/premortem`, `.bob/skills/hackathon-plan`, `.bob/skills/judge-review`
- Subagents (Claude Code): `.claude/agents/planner.md`, `premortem-critic.md`, `judge.md`
- Re-run `premortem-critic` at hour 24 and before submitting; run `judge` on the final README and video script.
