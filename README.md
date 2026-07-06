# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

```
Today's Schedule
====================
Scheduled tasks (65 min used):
- Morning walk (walk) - 30 min | priority: high | one-time | pending
- Feeding (feeding) - 15 min | priority: medium | one-time | pending
- Medication (medication) - 20 min | priority: low | one-time | pending

Reasoning:
Tasks were sorted by priority and scheduled until the 90-minute limit was reached. Included: Morning walk, Feeding, Medication. Skipped due to time: none.
```
## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

The scheduler now supports a few lightweight but useful planning behaviors:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_tasks()` and `Scheduler.sort_by_time()` | Tasks are ordered by priority first, then by time of day, duration, and task name. |
| Filtering behavior | `Scheduler.filter_tasks_by()` and `Scheduler.filter_tasks()` | The scheduler can filter tasks by completion status or pet name, and it only includes tasks that fit within the owner’s available time. |
| Conflict detection logic | `Scheduler._tasks_overlap()`, `Scheduler.find_conflicts()`, and `Scheduler.get_conflict_warning()` | The app detects overlapping task times and surfaces a clear warning message instead of crashing. |
| Recurring task logic | `Task.mark_completed()` | Completing a recurring task creates the next occurrence for daily or weekly repetition. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
