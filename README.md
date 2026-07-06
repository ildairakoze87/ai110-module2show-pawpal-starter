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

## Features

- Sorting by priority and time: tasks are ordered so the most urgent items appear first, then arranged by time of day.
- Chronological task ordering: tasks can also be viewed in strict time order for easier planning.
- Conflict warnings: overlapping tasks are detected and shown as warnings so the owner can adjust the schedule.
- Filtering by status or pet: pending tasks can be filtered by completion state or pet name.
- Daily recurrence: recurring tasks create a new occurrence for the next day or week when completed.

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

Run the full test suite with:

```bash
python -m pytest
```

These tests cover the core scheduler behaviors, including task updates, owner/pet task collection, chronological sorting, recurring-task creation, conflict detection for overlapping times, filtering by status or pet, and schedule generation for owners with and without tasks.

Confidence level: ⭐⭐⭐⭐☆ (4/5)

Sample test output:

```text
=================================== test session starts ===================================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.5.0
rootdir: /Users/ilda/Desktop/ai110-module2show-pawpal-starter
plugins: anyio-4.7.0
collected 12 items

test_pawpal_system.py ............                                                  [100%]

=================================== 12 passed in 0.02s ====================================
```

## 📐 Smarter Scheduling

The scheduler now supports a few lightweight but useful planning behaviors:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting behavior | `Scheduler.sort_tasks()` and `Scheduler.sort_by_time()` | Tasks are ordered by priority first, then by time of day, duration, and task name. |
| Filtering behavior | `Scheduler.filter_tasks_by()` and `Scheduler.filter_tasks()` | The scheduler can filter tasks by completion status or pet name, and it only includes tasks that fit within the owner’s available time. |
| Conflict detection logic | `Scheduler._tasks_overlap()`, `Scheduler.find_conflicts()`, and `Scheduler.get_conflict_warning()` | The app detects overlapping task times and surfaces a clear warning message instead of crashing. |
| Recurring task logic | `Task.mark_completed()` | Completing a recurring task creates the next occurrence for daily or weekly repetition. |

## 🎬 Demo Walkthrough

PawPal+ provides a simple, interactive flow for creating pet-care plans.

1. Open the Streamlit app and enter owner information, then add a pet such as Biscuit or Mochi.
2. Create one or more care tasks for that pet, including a title, duration, priority, and optional time.
3. Use the schedule button to generate a daily plan. The app shows the pending tasks in a sorted table and highlights any overlap warnings.
4. Review the generated schedule and the scheduler explanation to see which tasks were included and why.
5. If a recurring task is completed, the scheduler can create the next occurrence for the following day or week.

Example workflow:
- Add a pet → add a task such as a morning walk → generate the schedule → review the sorted tasks and any conflict warnings.

Key scheduler behaviors shown in the demo:
- Sorting by priority and time
- Conflict warnings when two tasks overlap
- Filtering of pending tasks and schedule generation within the owner’s available time
- Recurring-task generation after completion

Sample CLI output from running `main.py`:

```text
Unsorted tasks:
- Morning walk (07:00)
- Feeding (08:15)
- Grooming (07:00)
- Medication (09:30)

Sorted tasks by priority and time:
- Morning walk (07:00)
- Grooming (07:00)
- Feeding (08:15)
- Medication (09:30)

Conflicts:
Warning: Morning walk (07:00) overlaps with Grooming (07:00) for Biscuit and Biscuit.
```

**Screenshot or video** *(optional)*: You may add a screenshot here if you want a visual reviewer reference.
