---
name: premortem
description: Run a premortem on a plan, feature, or submission. Assume it already failed, list the most likely reasons, rank them by likelihood x impact, and turn the top ones into concrete preventive actions with owners and deadlines. Use before committing to a plan, before a demo or submission, or when the user asks "what could go wrong".
---

# Premortem

Imagine it is after the deadline and the project **failed**. Work backwards to why.

## Steps

1. **State the goal and the failure.** One line each. Example: "Goal: place top 3. Failure: not shortlisted."
2. **Generate failure causes.** Aim for 12 or more, across these lenses:
   - *Judges*: unclear value, weak demo, looks like every other entry, sponsor tech barely used.
   - *Product*: core feature doesn't work live, results look random, setup too hard.
   - *Execution*: scope too big, integration surprises (APIs, access, auth), time lost on polish.
   - *Submission*: late, missing video/repo/slides, broken links, private repo.
   - *External*: platform access delayed, rate limits, network, teammate unavailable.
3. **Score each cause** for likelihood (1-5) and impact (1-5). Sort by the product.
4. **For the top 5**, write one preventive action: what, who, by when, and how you'll know it worked.
5. **Name the tripwires**: an observable signal and a pre-agreed response (e.g. "if the live Bob demo isn't working by hour 30, record the demo from the CLI and cut the plugin").
6. **Change the plan.** A premortem that changes nothing was not done. List the edits to the plan.

## Output format

```
Goal / failure: ...
| # | Cause | L | I | LxI | Prevention (owner, deadline) |
Tripwires:
- signal -> response
Plan changes:
- ...
```

Be blunt. Prefer causes specific to this project over generic ones.
