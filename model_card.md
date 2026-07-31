# PawPal+ Model Card

## Project Overview
PawPal+ is an applied AI pet-care planning system that helps owners organize daily tasks such as walks, feeding, medication, and grooming. The system uses scheduling logic, retrieval-style guidance, logging, and reliability checks to produce a plan that is both useful and explainable.

## Limitations and Potential Biases
- The planner is deterministic rather than learned, so it does not adapt from historical owner behavior or long-term outcomes.
- The retrieval layer is a small built-in knowledge base, so recommendations reflect the categories encoded by the developer and may miss less common care contexts.
- The current priority scheme can over-emphasize explicit task labels and under-represent nuanced factors like pet temperament or multi-day health trends.
- Conflict detection is intentionally lightweight and checks direct time overlap rather than modeling richer constraints such as buffer times, travel time, or dependency chains.
- JSON persistence is simple and local, which is useful for coursework but limited for concurrent or multi-user environments.

## Misuse Risk and Prevention
Possible misuse includes treating the generated schedule as clinical advice or blindly following a plan without owner judgment. To reduce this risk, the system:

- Frames output as planning support rather than professional medical advice.
- Provides explicit reasoning and a planning log so users can inspect decisions.
- Flags conflicts and invalid inputs instead of silently failing.
- Keeps a human-in-the-loop feedback cycle where owners review and edit tasks/preferences.

## Reliability Testing Surprises
The most surprising result during reliability checks was how often small input-quality issues changed outcomes more than algorithm changes. Invalid times, invalid priorities, and malformed durations had a bigger effect on schedule quality than expected. After adding guardrails and normalization, the system became much more stable and test results were consistently reproducible.

## Collaboration with AI
I used AI as a design and implementation partner for class modeling, scheduler refinement, persistence scaffolding, and test planning.

### Helpful AI Suggestion
One helpful suggestion was to add guardrails for invalid task inputs (priority, duration, and time format) and then test those behaviors directly. This improved robustness and reduced runtime failures.

### Flawed or Incorrect AI Suggestion
One flawed suggestion was to keep explanation text separate from scheduling logic as a cosmetic output. That approach reduced trust because the explanation did not necessarily reflect the actual scheduling path. I corrected this by integrating retrieved guidance into schedule explanation generation and validating it with automated tests and CLI checks.