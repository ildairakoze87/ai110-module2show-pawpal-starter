# PawPal+ Model Card

## Project Overview
PawPal+ is an applied AI pet-care planning system that helps owners organize daily tasks such as walks, feeding, medication, and grooming. The system uses scheduling logic, retrieval-style guidance, logging, and reliability checks to produce a plan that is both useful and explainable.

## Responsible-AI Reflection
I collaborated with AI to brainstorm the class structure, refine scheduling logic, add persistence, and improve the explanation output. The most helpful AI suggestions were the ones that stayed close to the existing OOP design and proposed small, testable improvements, such as adding guardrails for invalid input and adding a reliability report.

One flawed suggestion was to treat the explanation text as a purely decorative output. In practice, the explanation needed to be integrated into the scheduling flow so it reflected actual planning decisions and could be verified in tests. I corrected that by making the guidance part of the scheduler explanation and by validating the behavior with `pytest` and CLI runs.

## System Limitations
- The planner is deterministic rather than learned, so it does not adapt from historical user behavior.
- The retrieval layer uses a small built-in knowledge base, not an external search engine or vector database.
- JSON persistence is simple and single-user oriented, so it is not designed for concurrent access.
- Conflict detection is lightweight and compares time slots directly instead of modeling a full calendar.

## Reliability and Verification
The system was verified with automated tests, a CLI run, and a guardrail check for invalid input. The final behavior includes a reliability snapshot and planning log so humans can inspect how the schedule was produced.

## What I Learned
This project showed me that AI is most useful when the human designer keeps the system focused, testable, and honest about its limits. AI can speed up implementation and help refine ideas, but the final responsibility is to verify behavior, keep the architecture coherent, and make sure the output is trustworthy.