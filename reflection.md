# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**My project classes description:** 

My initial UML design identifies five core classes representing the real-world objects in the PawPal+ system:

1. **Owner** – Stores owner information (name, available time, and preferences). Allows updating both time availability and preference settings.

2. **Pet** – Represents a pet with attributes like name, species, breed, and age. Can display and update pet information.

3. **Task** – Represents individual pet care tasks with properties including name, duration, priority level, category, and optional recurring/completion flags. Tasks can be edited, marked complete, and queried for details.

4. **Scheduler** – The core logic engine that manages the list of tasks and applies constraints. It sorts tasks by priority/constraints, filters applicable tasks, generates a complete daily schedule, and provides explanations for scheduling decisions.

5. **DailyPlan** – The output of the scheduler. Contains the scheduled tasks for the day, calculates time usage and remaining availability, and displays both the plan and the reasoning behind it.

**Relationships:**
- An Owner owns and manages a Pet
- An Owner uses the Scheduler to create plans
- A Pet requires various Tasks (e.g., feeding, walking, grooming)
- The Scheduler manages Task objects and generates a DailyPlan
- The DailyPlan is the final output showing scheduled_tasks, total_time_used, remaining_time, and explanation

This design separates concerns: Owner and Pet represent data entities, Task represents discrete units of work, Scheduler encapsulates the decision logic and constraints, and DailyPlan presents the results in a human-readable format.

**Three Core User Actions:**

1. **Add/Manage Pet and Owner Information** – Users should be able to create and update their profile (owner name, availability, preferences) and register their pet(s) with details like name, species, breed, and age. This establishes the context for the scheduler.

2. **Create and Manage Pet Care Tasks** – Users should be able to add, edit, and categorize pet care tasks (e.g., "morning walk," "feeding," "grooming"). Each task includes duration, priority level, and optional recurring settings. Users can also mark tasks as completed.

3. **Generate and View Daily Schedule** – Users should be able to request a daily plan that intelligently schedules their tasks based on available time, priority levels, and personal preferences. The system displays the optimized schedule, time allocation, and an explanation of why each task was included and when it was scheduled.



**b. Design changes**

Yes. I slightly adjusted the design to make the classes more self-contained. Instead of keeping most behavior in the scheduler alone, I gave each core object methods such as edit_task, mark_completed, update_pet_info, and update_available_time so that the data and actions stay together. This made the system easier to understand and use, and it also made the scheduler simpler because it could focus on planning rather than managing every update.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
