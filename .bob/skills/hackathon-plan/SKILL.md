---
name: hackathon-plan
description: Plan a time-boxed hackathon build. Turns an idea into a demo-first, hour-by-hour plan with a hard scope cut line, checkpoints, and a submission checklist. Use at kickoff, when re-planning mid-event, or when the user asks what to build next with limited time.
---

# Hackathon plan

Plan backwards from the **demo**, not forwards from the architecture.

## Steps

1. **Write the 3-minute demo script first.** Problem (20s), live demo (2 min), proof/numbers (30s), ask (10s). Every feature not on screen in that script is out of scope.
2. **Define the golden path.** The single sequence of commands/clicks the demo runs. It must work end to end by the midpoint.
3. **Split scope into three lines:**
   - *Must* (golden path works, recorded video, repo public, submission form done)
   - *Should* (the thing that makes it stand out: a metric, a visual, sponsor tech used deeply)
   - *Could* (everything else; do not start until Should is done)
4. **Timebox.** For a 48h event: 0-4h setup and golden-path skeleton; 4-24h make it real; 24-30h checkpoint (cut ruthlessly); 30-40h Should items and benchmark; 40-44h record video, slides, README; 44-48h submit early, then only fix typos.
5. **Checkpoints.** At each one ask: is the golden path still green? What is the biggest remaining risk? Cut what threatens the Must line.
6. **Submission checklist:** title, one-line pitch, long description, public repo with README and run instructions, demo video (under the length limit), slides, sponsor tech clearly named, team members added.

Run the `premortem` skill on the plan before starting and again at the midpoint checkpoint.
