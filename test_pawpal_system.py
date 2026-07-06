from datetime import timedelta

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


def test_scheduler_sort_by_time_orders_tasks_chronologically():
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


def test_recurring_task_creates_next_occurrence_when_completed():
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
