from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Maria", "90")

    biscuit = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    mochi = Pet("Mochi", "Cat", "Siamese", 2)

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 30, "high", "walk", time_of_day="07:00"))
    biscuit.add_task(Task("Feeding", 15, "medium", "feeding", time_of_day="08:15"))
    recurring_task = Task(
        "Medication",
        20,
        "low",
        "medication",
        time_of_day="09:30",
        recurring=True,
        recurrence="daily",
    )
    mochi.add_task(recurring_task)

    scheduler = Scheduler(owner.available_time)
    scheduler.load_tasks_from_owner(owner)

    print("Unsorted tasks:")
    for task in scheduler.list_of_tasks:
        print(f"- {task.task_name} ({task.time_of_day})")

    scheduler.sort_tasks()
    print("\nSorted tasks by priority and time:")
    for task in scheduler.list_of_tasks:
        print(f"- {task.task_name} ({task.time_of_day})")

    filtered_tasks = scheduler.filter_tasks_by(pet_name="biscuit")
    print("\nFiltered tasks for Biscuit:")
    for task in filtered_tasks:
        print(f"- {task.task_name}")

    next_occurrence = recurring_task.mark_completed()
    print("\nCompleted recurring task:")
    print(f"- Original: {recurring_task.get_task_details()}")
    if next_occurrence is not None:
        print(f"- Next occurrence: {next_occurrence.get_task_details()}")

    plan = scheduler.generate_schedule()

    print("\nToday's Schedule")
    print("=" * 20)
    print(plan.display_plan())
    print("\nReasoning:")
    print(plan.display_explanation())


if __name__ == "__main__":
    main()
