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
garner index --lib ./skill-library
garner pick "modernize PAYROLL.cbl to Java with tests" --repo ./payroll-demo
garner install "modernize PAYROLL.cbl to Java with tests" --repo ./payroll-demo --target bob
# In Bob: run the same task; the installed squad does the work
```

## Planning tools in this repo

- Skills (Bob and Claude Code): `.bob/skills/premortem`, `.bob/skills/hackathon-plan`, `.bob/skills/judge-review`
- Subagents (Claude Code): `.claude/agents/planner.md`, `premortem-critic.md`, `judge.md`
- Re-run `premortem-critic` at hour 24 and before submitting; run `judge` on the final README and video script.
