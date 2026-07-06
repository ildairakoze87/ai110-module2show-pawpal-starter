from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


# ─── TASK ───────────────────────────────────────────────────────────────────
@dataclass
class Task:
    task_name: str              # e.g. "Morning Walk"
    duration: int               # in minutes
    priority: str               # "high", "medium", or "low"
    category: str               # e.g. "walk", "feeding", "medication"
    recurring: bool = False     # does it repeat daily?
    completed: bool = False     # has it been done today?
    time_of_day: str = "00:00"  # e.g. "07:30"
    recurrence: str = ""       # "daily" or "weekly"
    due_date: datetime = field(default_factory=lambda: datetime.now().date())
    pet_name: str = ""          # pet that owns this task

    def edit_task(self, task_name: str = None, duration: int = None,
                  priority: str = None, category: str = None,
                  time_of_day: str = None) -> None:
        """Edit one or more fields of this task."""
        if task_name is not None:
            self.task_name = task_name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority.lower()
        if category is not None:
            self.category = category
        if time_of_day is not None:
            self.time_of_day = time_of_day

    def mark_completed(self):
        """Mark this task as completed and create the next recurring occurrence if needed."""
        self.completed = True

        if self.recurring:
            frequency = self.recurrence.lower() if self.recurrence else "daily"
            if frequency in {"daily", "weekly"}:
                next_due_date = self.due_date + timedelta(days=1) if frequency == "daily" else self.due_date + timedelta(weeks=1)
                return Task(
                    task_name=self.task_name,
                    duration=self.duration,
                    priority=self.priority,
                    category=self.category,
                    recurring=self.recurring,
                    completed=False,
                    time_of_day=self.time_of_day,
                    recurrence=frequency,
                    due_date=next_due_date,
                )
        return None

    def get_task_details(self) -> str:
        """Return a readable string summary of this task."""
        status = "completed" if self.completed else "pending"
        recurring_text = "recurring" if self.recurring else "one-time"
        return (
            f"{self.task_name} ({self.category}) - {self.duration} min | "
            f"priority: {self.priority} | {recurring_text} | {status} | time: {self.time_of_day}"
        )


# ─── PET ────────────────────────────────────────────────────────────────────
@dataclass
class Pet:
    pet_name: str               # e.g. "Biscuit"
    species: str                # e.g. "Dog"
    breed: str                  # e.g. "Golden Retriever"
    age: int                    # in years
    tasks: List[Task] = field(default_factory=list)

    def update_pet_info(self, pet_name: str = None, species: str = None,
                        breed: str = None, age: int = None) -> None:
        """Update one or more fields of this pet's info."""
        if pet_name is not None:
            self.pet_name = pet_name
        if species is not None:
            self.species = species
        if breed is not None:
            self.breed = breed
        if age is not None:
            self.age = age

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's care list."""
        task.pet_name = self.pet_name
        self.tasks.append(task)

    def display_pet_info(self) -> str:
        """Return a readable string summary of this pet."""
        return (
            f"{self.pet_name} is a {self.age}-year-old {self.breed} {self.species} "
            f"with {len(self.tasks)} task(s) planned."
        )


# ─── OWNER ──────────────────────────────────────────────────────────────────
@dataclass
class Owner:
    owner_name: str             # e.g. "Maria"
    available_time: str         # e.g. "120" minutes available today
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def update_available_time(self, new_time: str) -> None:
        """Update the owner's available time for the day."""
        self.available_time = new_time

    def update_preferences(self, new_preferences: dict) -> None:
        """Update the owner's scheduling preferences."""
        self.preferences.update(new_preferences)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return every task belonging to the owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


# ─── DAILY PLAN ─────────────────────────────────────────────────────────────

@dataclass
class DailyPlan:
    scheduled_tasks: List[Task] = field(default_factory=list)
    total_time_used: int = 0    # total minutes used by scheduled tasks
    remaining_time: int = 0     # minutes still available after scheduling
    explanation: str = ""       # reason why tasks were arranged this way

    def display_plan(self) -> str:
        """Return a readable string of the full daily plan."""
        if not self.scheduled_tasks:
            return "No tasks scheduled for today."

        lines = [f"Scheduled tasks ({self.total_time_used} min used):"]
        for task in self.scheduled_tasks:
            lines.append(f"- {task.get_task_details()}")
        return "\n".join(lines)

    def display_explanation(self) -> str:
        """Return the explanation of why the plan was built this way."""
        return self.explanation or "No explanation available."

    def calculate_remaining_time(self) -> int:
        """Calculate and return how many minutes are left after scheduling."""
        return self.remaining_time


# ─── SCHEDULER ──────────────────────────────────────────────────────────────

class Scheduler:
    def __init__(self, available_time: str):
        """Initialize the scheduler with available time and empty task lists."""
        self.list_of_tasks: List[Task] = []     # all tasks to consider
        self.available_time: str = available_time
        self.available_time_minutes: int = self._parse_available_time(available_time)
        self.scheduled_tasks: List[Task] = []   # tasks that fit in the plan
        self.skipped_tasks: List[Task] = []     # tasks that didn't fit
        self.conflicts: List[tuple[Task, Task]] = []

    def _parse_available_time(self, available_time: str) -> int:
        """Convert a string like '120' or '120 minutes' into an integer."""
        if isinstance(available_time, int):
            return available_time
        if not isinstance(available_time, str):
            return 0

        digits = "".join(char for char in available_time if char.isdigit())
        return int(digits) if digits else 0

    def load_tasks_from_owner(self, owner: Owner) -> None:
        """Retrieve all incomplete tasks from the owner's pets."""
        self.list_of_tasks = [task for task in owner.get_all_tasks() if not task.completed]

    def _parse_time(self, time_value: str) -> int:
        """Convert an HH:MM string into total minutes for sorting."""
        try:
            hours_str, minutes_str = time_value.split(":")
            return int(hours_str) * 60 + int(minutes_str)
        except (AttributeError, ValueError):
            return 0

    def sort_tasks(self) -> None:
        """Sort tasks by priority, then by time, duration, and name for a stable plan."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        self.list_of_tasks.sort(
            key=lambda task: (
                priority_rank.get(task.priority.lower(), 99),
                self._parse_time(getattr(task, "time_of_day", "00:00")),
                task.duration,
                task.task_name.lower(),
            )
        )

    def sort_by_time(self) -> None:
        """Sort tasks chronologically by their scheduled time of day."""
        self.list_of_tasks.sort(
            key=lambda task: self._parse_time(getattr(task, "time_of_day", "00:00"))
        )

    def filter_tasks_by(self, completed: bool = None, pet_name: str = None) -> List[Task]:
        """Return tasks filtered by completion state and/or pet name."""
        filtered_tasks: List[Task] = []
        for task in self.list_of_tasks:
            if completed is not None and task.completed != completed:
                continue
            if pet_name is not None and pet_name not in task.task_name.lower():
                continue
            filtered_tasks.append(task)
        return filtered_tasks

    def _tasks_overlap(self, first: Task, second: Task) -> bool:
        """Return True when two tasks share any time span in the day."""
        start_one = self._parse_time(getattr(first, "time_of_day", "00:00"))
        end_one = start_one + getattr(first, "duration", 0)
        start_two = self._parse_time(getattr(second, "time_of_day", "00:00"))
        end_two = start_two + getattr(second, "duration", 0)
        return start_one < end_two and start_two < end_one

    def find_conflicts(self) -> List[tuple[Task, Task]]:
        """Return every overlapping task pair found in the current task list."""
        conflicts: List[tuple[Task, Task]] = []
        for index, first_task in enumerate(self.list_of_tasks):
            for second_task in self.list_of_tasks[index + 1:]:
                if self._tasks_overlap(first_task, second_task):
                    conflicts.append((first_task, second_task))
        self.conflicts = conflicts
        return conflicts

    def get_conflict_warning(self) -> str:
        """Return a friendly warning message describing any detected task conflicts."""
        if not self.conflicts:
            return "No time conflicts detected."

        conflict_lines = []
        for first_task, second_task in self.conflicts:
            pet_label = first_task.pet_name or "unknown pet"
            other_pet = second_task.pet_name or "unknown pet"
            conflict_lines.append(
                f"{first_task.task_name} ({first_task.time_of_day}) overlaps with {second_task.task_name} ({second_task.time_of_day}) for {pet_label} and {other_pet}."
            )
        return "Warning: " + " | ".join(conflict_lines)

    def filter_tasks(self) -> List[Task]:
        """Place tasks into the scheduled list when they fit within the available time."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        remaining_time = self.available_time_minutes

        for task in self.list_of_tasks:
            if task.duration <= remaining_time:
                self.scheduled_tasks.append(task)
                remaining_time -= task.duration
            else:
                self.skipped_tasks.append(task)

        return self.scheduled_tasks

    def generate_schedule(self) -> DailyPlan:
        """Build a daily plan from sorted tasks that fit within the allowed time."""
        self.sort_tasks()
        self.filter_tasks()
        self.find_conflicts()

        total_time_used = sum(task.duration for task in self.scheduled_tasks)
        remaining_time = self.available_time_minutes - total_time_used
        plan = DailyPlan(
            scheduled_tasks=list(self.scheduled_tasks),
            total_time_used=total_time_used,
            remaining_time=remaining_time,
            explanation=self.explain_schedule(),
        )
        return plan

    def explain_schedule(self) -> str:
        """Return a short explanation of which tasks were included or skipped."""
        if not self.list_of_tasks:
            return "No tasks were available to schedule."

        included = ", ".join(task.task_name for task in self.scheduled_tasks) or "none"
        skipped = ", ".join(task.task_name for task in self.skipped_tasks) or "none"
        return (
            f"Tasks were sorted by priority and scheduled until the {self.available_time_minutes}-minute "
            f"limit was reached. Included: {included}. Skipped due to time: {skipped}."
        )


