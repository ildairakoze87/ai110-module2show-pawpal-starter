from datetime import timedelta
import json

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_methods_update_and_report_status():
    task = Task("Morning Walk", 30, "high", "walk")

    task.edit_task(duration=45, priority="medium")
    task.mark_completed()

    assert task.duration == 45
    assert task.priority == "medium"
    assert task.completed is True
    assert "Morning Walk" in task.get_task_details()
    assert "completed" in task.get_task_details()


def test_owner_collects_tasks_from_all_pets():
    owner = Owner("Maria", "90")
    pet_one = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    pet_two = Pet("Mochi", "Cat", "Siamese", 2)

    owner.add_pet(pet_one)
    owner.add_pet(pet_two)

    pet_one.add_task(Task("Walk", 30, "high", "walk"))
    pet_two.add_task(Task("Feed", 10, "medium", "feeding"))

    all_tasks = owner.get_all_tasks()

    assert len(all_tasks) == 2
    assert [task.task_name for task in all_tasks] == ["Walk", "Feed"]


def test_task_completion_marks_task_completed():
    task = Task("Play time", 20, "low", "play")
    assert task.completed is False

    task.mark_completed()

    assert task.completed is True


def test_pet_add_task_increments_task_count():
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, "high", "feeding"))

    assert len(pet.tasks) == 1


def test_sorting_correctness_returns_tasks_in_chronological_order():
    scheduler = Scheduler("90")
    scheduler.list_of_tasks = [
        Task("Medication", 20, "low", "medication", time_of_day="09:30"),
        Task("Morning walk", 30, "high", "walk", time_of_day="07:00"),
        Task("Feeding", 10, "medium", "feeding", time_of_day="08:15"),
    ]

    scheduler.sort_by_time()

    assert [task.task_name for task in scheduler.list_of_tasks] == [
        "Morning walk",
        "Feeding",
        "Medication",
    ]


def test_recurrence_logic_creates_next_day_task_when_daily_task_is_completed():
    task = Task("Medication", 10, "high", "medication", recurring=True, recurrence="daily")

    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.recurrence == "daily"
    assert next_task.task_name == "Medication"
    assert next_task.due_date == task.due_date + timedelta(days=1)


def test_scheduler_detects_conflicting_tasks_for_same_or_different_pets():
    scheduler = Scheduler("90")
    first_task = Task("Morning walk", 30, "high", "walk", time_of_day="07:00")
    second_task = Task("Feeding", 15, "medium", "feeding", time_of_day="07:00")
    first_task.pet_name = "Biscuit"
    second_task.pet_name = "Mochi"
    scheduler.list_of_tasks = [first_task, second_task]

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert conflicts[0][0] is first_task
    assert conflicts[0][1] is second_task


def test_scheduler_warning_message_mentions_conflicts():
    scheduler = Scheduler("90")
    first_task = Task("Morning walk", 30, "high", "walk", time_of_day="07:00")
    second_task = Task("Grooming", 10, "medium", "grooming", time_of_day="07:00")
    first_task.pet_name = "Biscuit"
    second_task.pet_name = "Biscuit"
    scheduler.list_of_tasks = [first_task, second_task]

    scheduler.find_conflicts()
    warning = scheduler.get_conflict_warning()

    assert "Warning:" in warning
    assert "Morning walk" in warning
    assert "Grooming" in warning


def test_scheduler_builds_plan_from_owner_tasks():
    owner = Owner("Maria", "90")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)

    pet.add_task(Task("Morning walk", 40, "high", "walk"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding"))
    pet.add_task(Task("Medication", 20, "low", "medication"))

    scheduler = Scheduler("90")
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    assert [task.task_name for task in plan.scheduled_tasks] == ["Morning walk", "Feeding", "Medication"]
    assert plan.total_time_used == 75
    assert plan.remaining_time == 15
    assert "Medication" in plan.explanation


def test_filter_tasks_by_handles_empty_results_and_pet_filtering():
    scheduler = Scheduler("90")
    tasks = [
        Task("Morning walk", 30, "high", "walk", time_of_day="07:00"),
        Task("Feeding", 15, "medium", "feeding", time_of_day="08:15"),
    ]
    tasks[0].completed = True
    scheduler.list_of_tasks = tasks

    pending_tasks = scheduler.filter_tasks_by(completed=False)
    pet_filtered = scheduler.filter_tasks_by(pet_name="biscuit")

    assert [task.task_name for task in pending_tasks] == ["Feeding"]
    assert pet_filtered == []


def test_scheduler_handles_pet_with_no_tasks():
    owner = Owner("Maria", "90")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)

    scheduler = Scheduler("90")
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    assert plan.scheduled_tasks == []
    assert plan.total_time_used == 0
    assert plan.remaining_time == 90


def test_conflict_detection_flags_duplicate_times():
    scheduler = Scheduler("90")
    first_task = Task("Morning walk", 30, "high", "walk", time_of_day="07:00")
    second_task = Task("Grooming", 10, "medium", "grooming", time_of_day="07:00")
    scheduler.list_of_tasks = [first_task, second_task]

    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 1
    assert conflicts[0][0] is first_task
    assert conflicts[0][1] is second_task


def test_task_guardrails_normalize_invalid_inputs():
    task = Task("Bad task", -5, "urgent", "walk", time_of_day="77:77")

    assert task.duration == 1
    assert task.priority == "medium"
    assert task.time_of_day == "00:00"


def test_owner_save_and_load_json_round_trip(tmp_path):
    file_path = tmp_path / "owner_data.json"
    owner = Owner("Ava", "60")
    pet = Pet("Nori", "Dog", "Corgi", 4)
    pet.add_task(Task("Lunch", 15, "high", "feeding", time_of_day="12:00"))
    owner.add_pet(pet)

    owner.save_to_json(str(file_path))
    loaded = Owner.load_from_json(str(file_path))

    assert loaded.owner_name == "Ava"
    assert len(loaded.pets) == 1
    assert loaded.pets[0].pet_name == "Nori"
    assert loaded.pets[0].tasks[0].task_name == "Lunch"


def test_scheduler_explanation_includes_retrieved_guidance():
    owner = Owner("Maria", "30")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)
    pet.add_task(Task("Medication", 10, "high", "medication", time_of_day="09:00"))

    scheduler = Scheduler(owner.available_time)
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    assert "Guidance used:" in plan.explanation
    assert "Medication" in plan.explanation


def test_scheduler_reliability_report_counts_tasks_and_conflicts():
    scheduler = Scheduler("15")
    first_task = Task("Walk", 10, "high", "walk", time_of_day="07:00")
    second_task = Task("Feeding", 10, "medium", "feeding", time_of_day="07:05")
    scheduler.list_of_tasks = [first_task, second_task]

    scheduler.generate_schedule()
    report = scheduler.reliability_report()

    assert report["total_tasks"] == 2
    assert report["scheduled_tasks"] == 1
    assert report["skipped_tasks"] == 1
    assert report["conflicts"] == 1


def test_scheduler_uses_custom_retrieval_document_guidance(tmp_path):
    retrieval_file = tmp_path / "retrieval_guidance.json"
    retrieval_file.write_text(
        json.dumps(
            {
                "category_guidance": {
                    "feeding": "Custom feeding rule from document source."
                }
            }
        ),
        encoding="utf-8",
    )

    owner = Owner("Maria", "30")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)
    pet.add_task(Task("Feeding", 10, "high", "feeding", time_of_day="08:00"))

    scheduler = Scheduler(owner.available_time, retrieval_file_path=str(retrieval_file))
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    assert "Custom feeding rule from document source." in plan.explanation


def test_owner_preference_guidance_overrides_custom_document(tmp_path):
    retrieval_file = tmp_path / "retrieval_guidance.json"
    retrieval_file.write_text(
        json.dumps(
            {
                "category_guidance": {
                    "medication": "Custom medication rule from document source."
                }
            }
        ),
        encoding="utf-8",
    )

    owner = Owner(
        "Maria",
        "30",
        preferences={
            "category_guidance": {
                "medication": "Owner preference: prioritize medication before other tasks."
            }
        },
    )
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)
    pet.add_task(Task("Medication", 10, "high", "medication", time_of_day="09:00"))

    scheduler = Scheduler(owner.available_time, retrieval_file_path=str(retrieval_file))
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    assert "Owner preference: prioritize medication before other tasks." in plan.explanation


def test_scheduler_decision_trace_records_multistep_reasoning_and_saves(tmp_path):
    owner = Owner("Maria", "30")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 20, "high", "walk", time_of_day="07:00"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding", time_of_day="08:00"))

    scheduler = Scheduler(owner.available_time)
    scheduler.load_tasks_from_owner(owner)
    scheduler.generate_schedule()

    trace_steps = [entry["step"] for entry in scheduler.get_decision_trace()]
    assert "load_tasks" in trace_steps
    assert "start_generate_schedule" in trace_steps
    assert "sort_tasks" in trace_steps
    assert "filter_tasks" in trace_steps
    assert "find_conflicts" in trace_steps
    assert "final_plan" in trace_steps

    trace_file = tmp_path / "decision_trace.json"
    scheduler.save_decision_trace(str(trace_file))
    assert trace_file.exists()
