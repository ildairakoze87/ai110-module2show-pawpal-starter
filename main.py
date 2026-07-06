from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Maria", "90")

    biscuit = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    mochi = Pet("Mochi", "Cat", "Siamese", 2)

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", 30, "high", "walk"))
    biscuit.add_task(Task("Feeding", 15, "medium", "feeding"))
    mochi.add_task(Task("Medication", 20, "low", "medication"))

    scheduler = Scheduler(owner.available_time)
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()

    print("Today's Schedule")
    print("=" * 20)
    print(plan.display_plan())
    print("\nReasoning:")
    print(plan.display_explanation())


if __name__ == "__main__":
    main()
