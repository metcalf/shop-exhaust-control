# Process Notes

Lessons from running this project with a Claude supervisor and subagents, to carry into the dust collector project. Add an entry whenever something about the process works well or badly: a gate that caught a real problem, a subagent brief that was too vague, a phase that ate far more sessions than expected, a question that should have been asked earlier.

Format: date, phase, what happened, what to change.

---

- **2026-10-23, setup.** The kickoff docs said Andrew does HVLP spraying; he doesn't (aerosol cans only). The error drove a non-negotiable safety rule, a hardware spray bypass and a vapor-rated fan requirement. **Change:** in kickoff docs, mark facts about the owner and site as *stated* or *inferred*, and confirm inferred ones before building requirements or safety rules on them.
- **2026-10-24, setup (tooling, D-010).** Chose tools to make Claude's weak areas checkable instead of trusted: rendered schematic/board images, scripted netlist assertions against datasheets, creepage as a DRC rule. **Carry forward:** for the DC controller, reuse the netlist-assertion script and DRC rule file, and use the phase 3 Freerouting-vs-Quilter result to pick one layout path. *(Fill in the outcome after phase 3.)*
- **2026-10-25, phase 0→1.** The survey showed the fan's 120 V is switched by the lighting relay, so the fan dies when the lights go off. D-009 (vacant clear-down) had been accepted without knowing that. **Change:** for the DC project, the survey should ask early, for every load and every signal: how is it powered and switched today, and what turns it off? Check accepted behavior decisions against the answers before writing requirements.
- **2026-10-25, phase 1.** Putting thresholds in a parameter table (`P-nn`) with initial values and their sources let every AC be concrete enough to host-test now, while still leaving final values to commissioning. **Carry forward** to the DC project.
