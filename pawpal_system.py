import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple


logger = logging.getLogger("pawpal")


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
    due_date: date = field(default_factory=lambda: datetime.now().date())
    pet_name: str = ""          # pet that owns this task

    VALID_PRIORITIES = {"high", "medium", "low"}

    def __post_init__(self) -> None:
        """Normalize and guardrail task input so scheduling remains safe."""
        self.priority = (self.priority or "medium").lower()
        if self.priority not in self.VALID_PRIORITIES:
            logger.warning("Unknown priority '%s'. Falling back to 'medium'.", self.priority)
            self.priority = "medium"

        if not isinstance(self.duration, int) or self.duration <= 0:
            logger.warning("Invalid duration '%s'. Falling back to 1 minute.", self.duration)
            self.duration = 1

        if not self._is_valid_time(self.time_of_day):
            logger.warning("Invalid time_of_day '%s'. Falling back to 00:00.", self.time_of_day)
            self.time_of_day = "00:00"

        if isinstance(self.due_date, datetime):
            self.due_date = self.due_date.date()

    @staticmethod
    def _is_valid_time(time_value: str) -> bool:
        """Return True only for HH:MM values in 24-hour format."""
        try:
            if not isinstance(time_value, str):
                return False
            parts = time_value.split(":")
            if len(parts) != 2:
                return False
            hours = int(parts[0])
            minutes = int(parts[1])
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except ValueError:
            return False

    def edit_task(self, task_name: str = None, duration: int = None,
                  priority: str = None, category: str = None,
                  time_of_day: str = None) -> None:
        """Edit one or more fields of this task."""
        if task_name is not None:
            self.task_name = task_name
        if duration is not None:
            self.duration = duration if duration > 0 else 1
        if priority is not None:
            normalized = priority.lower()
            self.priority = normalized if normalized in self.VALID_PRIORITIES else "medium"
        if category is not None:
            self.category = category
        if time_of_day is not None and self._is_valid_time(time_of_day):
            self.time_of_day = time_of_day

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this task for JSON persistence."""
        return {
            "task_name": self.task_name,
            "duration": self.duration,
            "priority": self.priority,
            "category": self.category,
            "recurring": self.recurring,
            "completed": self.completed,
            "time_of_day": self.time_of_day,
            "recurrence": self.recurrence,
            "due_date": self.due_date.isoformat(),
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize a task from JSON-safe data."""
        raw_due_date = data.get("due_date", datetime.now().date().isoformat())
        try:
            parsed_due_date = date.fromisoformat(str(raw_due_date))
        except ValueError:
            parsed_due_date = datetime.now().date()

        return cls(
            task_name=data.get("task_name", "Untitled Task"),
            duration=int(data.get("duration", 1)),
            priority=data.get("priority", "medium"),
            category=data.get("category", "general"),
            recurring=bool(data.get("recurring", False)),
            completed=bool(data.get("completed", False)),
            time_of_day=data.get("time_of_day", "00:00"),
            recurrence=data.get("recurrence", ""),
            due_date=parsed_due_date,
            pet_name=data.get("pet_name", ""),
        )

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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this pet and its tasks."""
        return {
            "pet_name": self.pet_name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """Deserialize a pet and nested tasks."""
        pet = cls(
            pet_name=data.get("pet_name", "Unnamed Pet"),
            species=data.get("species", "other"),
            breed=data.get("breed", "Unknown"),
            age=int(data.get("age", 0)),
        )
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize owner profile and nested pets/tasks."""
        return {
            "owner_name": self.owner_name,
            "available_time": self.available_time,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Owner":
        """Deserialize owner profile from JSON-safe data."""
        owner = cls(
            owner_name=data.get("owner_name", "Owner"),
            available_time=str(data.get("available_time", "120")),
            preferences=dict(data.get("preferences", {})),
        )
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, file_path: str = "data.json") -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        path = Path(file_path)
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)
        logger.info("Saved owner data to %s", path)

    @classmethod
    def load_from_json(cls, file_path: str = "data.json") -> "Owner":
        """Load persisted owner data or return a safe default owner."""
        path = Path(file_path)
        if not path.exists():
            logger.info("No data file found at %s; using default owner.", path)
            return cls("Jordan", "120")

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        logger.info("Loaded owner data from %s", path)
        return cls.from_dict(data)


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
    DEFAULT_RETRIEVAL_FILE = "retrieval_guidance.json"

    KNOWLEDGE_BASE = {
        "medication": "Medication tasks should happen as close as possible to their planned time.",
        "feeding": "Feeding should be consistent day to day to avoid stomach upset.",
        "walk": "Walk tasks are higher value earlier in the day when possible.",
        "grooming": "Grooming can be delayed if higher-risk care tasks need time first.",
        "general": "General care tasks are scheduled after higher-priority essentials.",
    }

    CATEGORY_BOOST = {
        "medication": 0,
        "feeding": 1,
        "walk": 1,
        "grooming": 2,
        "general": 3,
    }

    FEW_SHOT_STYLE_PATTERNS = {
        "clinical_compact": {
            "label": "Clinical Compact",
            "header": "Care Plan Summary",
            "line_template": "- {task_name} at {time_of_day}: {guidance}",
            "footer": "Risk: {risk_level} | Confidence: {confidence}",
        },
        "coach_supportive": {
            "label": "Coach Supportive",
            "header": "Pet Care Coaching Note",
            "line_template": "- {task_name} ({time_of_day}): Focus on consistency. {guidance}",
            "footer": "Consistency score: {confidence} | Keep iterating based on daily feedback.",
        },
    }

    def __init__(self, available_time: str, retrieval_file_path: str = None):
        """Initialize the scheduler with available time and empty task lists."""
        self.list_of_tasks: List[Task] = []     # all tasks to consider
        self.available_time: str = available_time
        self.available_time_minutes: int = self._parse_available_time(available_time)
        self.scheduled_tasks: List[Task] = []   # tasks that fit in the plan
        self.skipped_tasks: List[Task] = []     # tasks that didn't fit
        self.conflicts: List[tuple[Task, Task]] = []
        self.planning_log: List[str] = []
        self.decision_trace: List[Dict[str, Any]] = []
        self.custom_category_guidance: Dict[str, str] = {}
        self.custom_task_guidance: Dict[str, str] = {}
        self.owner_category_guidance: Dict[str, str] = {}
        self.owner_task_guidance: Dict[str, str] = {}
        self.explanation_style: str = "baseline"

        default_path = retrieval_file_path or self.DEFAULT_RETRIEVAL_FILE
        self.load_custom_retrieval_documents(default_path)

    def _record_trace(self, step: str, details: Dict[str, Any]) -> None:
        """Record structured reasoning steps for audit and documentation."""
        self.decision_trace.append({"step": step, "details": details})

    def _parse_available_time(self, available_time: str) -> int:
        """Convert a string like '120' or '120 minutes' into an integer."""
        if isinstance(available_time, int):
            return available_time
        if not isinstance(available_time, str):
            logger.warning("Unexpected available_time type %s; using 0.", type(available_time).__name__)
            return 0

        digits = "".join(char for char in available_time if char.isdigit())
        if not digits:
            logger.warning("Could not parse available_time '%s'; using 0.", available_time)
            return 0
        return int(digits)

    def load_tasks_from_owner(self, owner: Owner) -> None:
        """Retrieve all incomplete tasks from the owner's pets."""
        self.list_of_tasks = [task for task in owner.get_all_tasks() if not task.completed]
        self._load_owner_guidance(owner.preferences)
        if isinstance(owner.preferences, dict):
            preferred_style = owner.preferences.get("explanation_style", "baseline")
            self.explanation_style = str(preferred_style)
        self.planning_log.append(f"Loaded {len(self.list_of_tasks)} pending task(s) from owner data.")
        self._record_trace(
            "load_tasks",
            {
                "pending_count": len(self.list_of_tasks),
                "tasks": [task.task_name for task in self.list_of_tasks],
            },
        )

    def load_custom_retrieval_documents(self, file_path: str) -> None:
        """Load optional retrieval guidance from a custom JSON document."""
        path = Path(file_path)
        if not path.exists():
            self.planning_log.append(f"No custom retrieval file found at {file_path}; using built-in guidance.")
            return

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("Could not load retrieval file '%s': %s", file_path, error)
            self.planning_log.append(f"Failed to load custom retrieval file at {file_path}; using built-in guidance.")
            return

        category_guidance = data.get("category_guidance", {})
        task_guidance = data.get("task_guidance", {})
        self.custom_category_guidance = {
            str(key).lower(): str(value) for key, value in category_guidance.items()
        }
        self.custom_task_guidance = {
            str(key).strip().lower(): str(value) for key, value in task_guidance.items()
        }
        self.planning_log.append(
            "Loaded custom retrieval guidance from document source."
        )
        self._record_trace(
            "load_custom_retrieval",
            {
                "category_guidance_count": len(self.custom_category_guidance),
                "task_guidance_count": len(self.custom_task_guidance),
            },
        )

    def _load_owner_guidance(self, preferences: Dict[str, Any]) -> None:
        """Load retrieval hints from owner preferences as a second source."""
        category_guidance = preferences.get("category_guidance", {}) if isinstance(preferences, dict) else {}
        task_guidance = preferences.get("task_guidance", {}) if isinstance(preferences, dict) else {}

        self.owner_category_guidance = {
            str(key).lower(): str(value) for key, value in category_guidance.items()
        }
        self.owner_task_guidance = {
            str(key).strip().lower(): str(value) for key, value in task_guidance.items()
        }
        if self.owner_category_guidance or self.owner_task_guidance:
            self.planning_log.append("Loaded owner-preference retrieval guidance.")
            self._record_trace(
                "load_owner_retrieval",
                {
                    "category_guidance_count": len(self.owner_category_guidance),
                    "task_guidance_count": len(self.owner_task_guidance),
                },
            )

    def _parse_time(self, time_value: str) -> int:
        """Convert an HH:MM string into total minutes for sorting."""
        try:
            hours_str, minutes_str = time_value.split(":")
            return int(hours_str) * 60 + int(minutes_str)
        except (AttributeError, ValueError):
            return 0

    def sort_tasks(self) -> None:
        """Sort tasks by priority, then retrieved category guidance, then time."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        self.list_of_tasks.sort(
            key=lambda task: (
                priority_rank.get(task.priority.lower(), 99),
                self.CATEGORY_BOOST.get(task.category.lower(), self.CATEGORY_BOOST["general"]),
                self._parse_time(getattr(task, "time_of_day", "00:00")),
                task.duration,
                task.task_name.lower(),
            )
        )
        self.planning_log.append("Sorted tasks by priority, category guidance, and time.")
        self._record_trace(
            "sort_tasks",
            {
                "sorted_order": [task.task_name for task in self.list_of_tasks],
            },
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
            if pet_name is not None and pet_name.lower() not in task.pet_name.lower():
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
        self.planning_log.append(f"Detected {len(conflicts)} conflict(s).")
        self._record_trace(
            "find_conflicts",
            {
                "conflict_count": len(conflicts),
                "pairs": [
                    {
                        "first": first.task_name,
                        "second": second.task_name,
                    }
                    for first, second in conflicts
                ],
            },
        )
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

        self.planning_log.append(
            f"Scheduled {len(self.scheduled_tasks)} task(s) and skipped {len(self.skipped_tasks)} due to time limit."
        )
        self._record_trace(
            "filter_tasks",
            {
                "scheduled": [task.task_name for task in self.scheduled_tasks],
                "skipped": [task.task_name for task in self.skipped_tasks],
                "time_limit_minutes": self.available_time_minutes,
            },
        )

        return self.scheduled_tasks

    def _retrieve_guidance_for_task(self, task: Task) -> str:
        """Retrieve guidance from multiple sources with deterministic precedence."""
        task_name = task.task_name.strip().lower()
        category = task.category.lower()

        if task_name in self.owner_task_guidance:
            return self.owner_task_guidance[task_name]
        if task_name in self.custom_task_guidance:
            return self.custom_task_guidance[task_name]
        if category in self.owner_category_guidance:
            return self.owner_category_guidance[category]
        if category in self.custom_category_guidance:
            return self.custom_category_guidance[category]
        return self.KNOWLEDGE_BASE.get(category, self.KNOWLEDGE_BASE["general"])

    def get_planning_log(self) -> List[str]:
        """Expose planning steps for UI and CLI transparency."""
        return list(self.planning_log)

    def get_decision_trace(self) -> List[Dict[str, Any]]:
        """Expose structured multi-step reasoning records."""
        return list(self.decision_trace)

    def save_decision_trace(self, file_path: str = "logs/reasoning_trace_latest.json") -> str:
        """Persist the structured decision trace to a JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(self.decision_trace, file, indent=2)
        self.planning_log.append(f"Saved decision trace to {path}")
        return str(path)

    def reliability_report(self) -> Dict[str, Any]:
        """Return simple reliability metrics to verify scheduler behavior."""
        total_tasks = len(self.list_of_tasks)
        scheduled_count = len(self.scheduled_tasks)
        skipped_count = len(self.skipped_tasks)
        coverage = (scheduled_count / total_tasks) if total_tasks else 0.0
        return {
            "total_tasks": total_tasks,
            "scheduled_tasks": scheduled_count,
            "skipped_tasks": skipped_count,
            "conflicts": len(self.conflicts),
            "coverage_ratio": round(coverage, 2),
        }

    def _baseline_explanation(self) -> str:
        """Return the original baseline explanation style."""
        included = ", ".join(task.task_name for task in self.scheduled_tasks) or "none"
        skipped = ", ".join(task.task_name for task in self.skipped_tasks) or "none"
        guidance_segments = []
        for task in self.scheduled_tasks:
            guidance_segments.append(f"{task.task_name}: {self._retrieve_guidance_for_task(task)}")
        guidance_text = " | ".join(guidance_segments) if guidance_segments else "none"

        return (
            f"Tasks were sorted by priority and scheduled until the {self.available_time_minutes}-minute "
            f"limit was reached. Included: {included}. Skipped due to time: {skipped}. "
            f"Guidance used: {guidance_text}."
        )

    def _risk_level(self) -> str:
        """Estimate risk from skipped tasks and detected conflicts."""
        if self.skipped_tasks or self.conflicts:
            return "elevated"
        return "low"

    def _confidence_score_text(self) -> str:
        """Compute a deterministic confidence score from schedule coverage and conflicts."""
        total_tasks = len(self.list_of_tasks)
        if total_tasks == 0:
            return "1.00"

        coverage = len(self.scheduled_tasks) / total_tasks
        conflict_penalty = 0.10 * len(self.conflicts)
        confidence = max(0.0, min(1.0, coverage - conflict_penalty))
        return f"{confidence:.2f}"

    def _specialized_explanation(self, style: str) -> str:
        """Generate constrained tone output using few-shot style templates."""
        profile = self.FEW_SHOT_STYLE_PATTERNS.get(style)
        if not profile:
            return self._baseline_explanation()

        lines = [f"{profile['header']} ({profile['label']})"]
        for task in self.scheduled_tasks:
            lines.append(
                profile["line_template"].format(
                    task_name=task.task_name,
                    time_of_day=task.time_of_day,
                    guidance=self._retrieve_guidance_for_task(task),
                )
            )

        if not self.scheduled_tasks:
            lines.append("- No scheduled tasks available.")

        lines.append(
            profile["footer"].format(
                risk_level=self._risk_level(),
                confidence=self._confidence_score_text(),
            )
        )
        if self.skipped_tasks:
            skipped = ", ".join(task.task_name for task in self.skipped_tasks)
            lines.append(f"Deferred tasks: {skipped}")
        return "\n".join(lines)

    @staticmethod
    def _explanation_metrics(text: str) -> Dict[str, Any]:
        """Return simple measurable stats for explanation comparison."""
        sentence_count = 0
        for marker in [".", "!", "?"]:
            sentence_count += text.count(marker)
        lines = [line for line in text.splitlines() if line.strip()]
        bullet_count = sum(1 for line in lines if line.strip().startswith("-"))
        return {
            "char_count": len(text),
            "line_count": len(lines),
            "sentence_markers": sentence_count,
            "bullet_count": bullet_count,
        }

    def compare_explanation_modes(self, specialized_style: str = "clinical_compact") -> Dict[str, Any]:
        """Compare baseline and specialized outputs with measurable metrics."""
        baseline_text = self._baseline_explanation()
        specialized_text = self._specialized_explanation(specialized_style)
        baseline_metrics = self._explanation_metrics(baseline_text)
        specialized_metrics = self._explanation_metrics(specialized_text)
        return {
            "baseline": {
                "style": "baseline",
                "text": baseline_text,
                "metrics": baseline_metrics,
            },
            "specialized": {
                "style": specialized_style,
                "text": specialized_text,
                "metrics": specialized_metrics,
            },
            "differences": {
                "char_delta": specialized_metrics["char_count"] - baseline_metrics["char_count"],
                "line_delta": specialized_metrics["line_count"] - baseline_metrics["line_count"],
                "bullet_delta": specialized_metrics["bullet_count"] - baseline_metrics["bullet_count"],
            },
        }

    def save_specialized_comparison(
        self,
        comparison: Dict[str, Any],
        file_path: str = "logs/specialized_behavior_report_latest.json",
    ) -> str:
        """Persist baseline-vs-specialized comparison for assignment evidence."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(comparison, file, indent=2)
        self.planning_log.append(f"Saved specialized behavior report to {path}")
        return str(path)

    def generate_schedule(self) -> DailyPlan:
        """Build a daily plan from sorted tasks that fit within the allowed time."""
        self._record_trace(
            "start_generate_schedule",
            {
                "available_time_minutes": self.available_time_minutes,
            },
        )
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
        self.planning_log.append("Generated daily plan object.")
        self._record_trace(
            "final_plan",
            {
                "total_time_used": total_time_used,
                "remaining_time": remaining_time,
            },
        )
        return plan

    def explain_schedule(self) -> str:
        """Return baseline or specialized explanation based on selected style."""
        if not self.list_of_tasks:
            return "No tasks were available to schedule."
        style_key = (self.explanation_style or "baseline").strip().lower()
        if style_key in self.FEW_SHOT_STYLE_PATTERNS:
            return self._specialized_explanation(style_key)
        return self._baseline_explanation()


