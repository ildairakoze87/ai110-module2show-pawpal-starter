# PawPal+ Applied AI System

## Title and Summary
PawPal+ is an applied AI pet-care planning system that helps owners organize daily care tasks such as walks, feeding, medication, and grooming. It matters because owners often have limited time and many competing tasks, so the system provides a prioritized schedule, conflict warnings, and a clear explanation of planning decisions. The project combines scheduling logic, retrieval-style guidance, reliability checks, and persistence so the system is both useful and trustworthy.

## Original Project (Modules 3(Show Pawpal starter))
The original project I extended is **PawPal+ (Module 2 Project)**. Its original goal was to model pet-care planning with OOP classes (`Owner`, `Pet`, `Task`, `Scheduler`, `DailyPlan`) and generate a daily schedule based on available time and task priority. It already supported priority/time sorting, recurrence handling, conflict detection, and CLI plus Streamlit demonstrations.

## Architecture Overview
The system diagram is in `diagrams/architecture.mmd`. The architecture has five main AI-system components:

1. **Retriever**: looks up category guidance (for example, medication timing consistency) before final explanation.
2. **Agent Planner**: schedules tasks using constraints, guardrails, and sorting logic.
3. **Evaluator**: produces reliability metrics and planning logs.
4. **Tester**: validates behavior through automated `pytest` checks.
5. **Human Review**: user inspects outputs and adjusts preferences/tasks.

Data flow is: **User Input -> Interface (CLI/Streamlit) -> Retriever + Planner -> Output Plan + Explanation -> Evaluator/Tester -> Human Feedback Loop**.

## Setup Instructions
Follow these steps from the project folder.

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run reliability tests.

```bash
python -m pytest -q
```

4. Run the CLI demo.

```bash
python main.py
```

5. Run the Streamlit app.

```bash
streamlit run app.py
```

Notes:
- The system automatically loads `data.json` if present.
- If `data.json` does not exist, a safe default owner profile is created.

## Sample Interactions
Below are representative examples showing the system behavior.

### Example 1: Priority + Time Planning
Input:
- Available time: 90 minutes
- Tasks:
  - Morning walk, 30 min, high, 07:00
  - Feeding, 15 min, medium, 08:15
  - Grooming, 10 min, medium, 07:00
  - Medication, 20 min, low, 09:30

AI output (CLI excerpt):

```text
Sorted tasks by priority and time:
- Morning walk (07:00)
- Feeding (08:15)
- Grooming (07:00)
- Medication (09:30)

Today's Schedule
====================
Scheduled tasks (75 min used):
- Morning walk (walk) - 30 min | priority: high | one-time | pending | time: 07:00
- Feeding (feeding) - 15 min | priority: medium | one-time | pending | time: 08:15
- Grooming (grooming) - 10 min | priority: medium | one-time | pending | time: 07:00
- Medication (medication) - 20 min | priority: low | recurring | completed | time: 09:30
```

### Example 2: Retrieval-Augmented Explanation
Input:
- Same scheduled tasks as above

AI output (reasoning excerpt):

```text
Guidance used: Morning walk: Walk tasks are higher value earlier in the day when possible. |
Feeding: Feeding should be consistent day to day to avoid stomach upset. |
Grooming: Grooming can be delayed if higher-risk care tasks need time first. |
Medication: Medication tasks should happen as close as possible to their planned time.
```

This shows retrieval is integrated into the plan explanation and not a separate script.

### Example 3: Reliability and Conflict Checks
Input:
- Two overlapping tasks at around 07:00

AI output:

```text
Conflicts:
Warning: Morning walk (07:00) overlaps with Grooming (07:00) for Biscuit and Biscuit.

Reliability snapshot:
{'total_tasks': 4, 'scheduled_tasks': 4, 'skipped_tasks': 0, 'conflicts': 1, 'coverage_ratio': 1.0}
```

## Design Decisions and Trade-offs
1. **Kept a deterministic planner instead of a heavy ML model**
	- Why: easier to test, reproduce, and debug in a course setting.
	- Trade-off: less adaptive than learned scheduling models.

2. **Added retrieval-style guidance through a knowledge base**
	- Why: lets the planner provide context-aware explanations.
	- Trade-off: fixed guidance rules are simpler but less expressive than external knowledge retrieval.

3. **Added strong input guardrails**
	- Why: invalid values should fail safely without crashing.
	- Trade-off: fallback normalization can hide data-entry mistakes if users do not inspect logs.

4. **Integrated reliability reporting and tests**
	- Why: final project requires trust and verification evidence.
	- Trade-off: adds complexity to output, but improves transparency.

5. **Added JSON persistence**
	- Why: practical user experience across runs.
	- Trade-off: file-based persistence is simple but not ideal for multi-user or concurrent access.

## Testing Summary
What worked: the full automated test suite passed, the CLI demo ran end to end, persistence saved the current state to `data.json`, and invalid task inputs were safely normalized instead of crashing the app.

What didn’t work : the first version of the scheduler explanation was more basic, and the system originally did not surface reliability metrics or a planner execution log in the main output.

The graded responsible-AI reflection for this project is documented in `model_card.md`, as required by the assignment.

## Reliability proof:
 **16 out of 16 tests passed**; the CLI run completed successfully; and guardrail checks showed that invalid values were safely corrected instead of causing failures. The planner also records an execution log and reliability snapshot, which makes it easier to review what happened and why.

> 16 out of 16 tests passed; the AI handled missing or invalid input by normalizing it; logging and the reliability snapshot made the run easy to review.

## Why This Meets the Applied AI Goal
PawPal+ now functions as an end-to-end applied AI system: it plans tasks under constraints, retrieves guidance to justify decisions, logs and evaluates reliability, and supports human review with iterative feedback.
