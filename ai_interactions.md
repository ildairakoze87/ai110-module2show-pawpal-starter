# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**
I asked the agent to implement multi-step reasoning with explicit planning steps and save intermediate reasoning traces to a committed log file, then document that workflow.

**What did the agent do?**
1. Added a structured decision trace pipeline in `Scheduler` (step + details entries).
2. Added trace persistence to JSON (`save_decision_trace`) in `pawpal_system.py`.
3. Updated `main.py` to save a run trace to `logs/reasoning_trace_latest.json`.
4. Added automated tests verifying trace generation and trace-file saving.
5. Ran the full suite and confirmed all tests pass.

**What did you have to verify or fix manually?**
I manually verified that the trace file was actually generated from a real CLI run and checked that the trace sequence reflected the scheduling workflow (load -> sort -> filter -> conflict check -> final plan).

### Intermediate Reasoning Trace (Embedded)

Trace log file: `logs/reasoning_trace_latest.json`

Excerpt:

```json
[
	{
		"step": "load_tasks",
		"details": {
			"pending_count": 3,
			"tasks": ["Morning walk", "Feeding", "Grooming"]
		}
	},
	{
		"step": "sort_tasks",
		"details": {
			"sorted_order": ["Morning walk", "Feeding", "Grooming"]
		}
	},
	{
		"step": "filter_tasks",
		"details": {
			"scheduled": ["Morning walk", "Feeding", "Grooming"],
			"skipped": [],
			"time_limit_minutes": 90
		}
	},
	{
		"step": "final_plan",
		"details": {
			"total_time_used": 55,
			"remaining_time": 35
		}
	}
]
```

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**
Not attempted for this extension.
