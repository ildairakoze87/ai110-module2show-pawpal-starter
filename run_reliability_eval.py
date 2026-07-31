import json
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from pawpal_system import Owner, Pet, Scheduler, Task


@dataclass
class EvalCase:
    name: str
    builder: Callable[[], Owner]
    expected_scheduled: Optional[int] = None
    expected_conflicts: Optional[int] = None
    expected_contains: Optional[str] = None


def _confidence_from_report(report: Dict[str, float]) -> float:
    """Use the same deterministic confidence logic used by scheduler explanations."""
    coverage = float(report.get("coverage_ratio", 0.0))
    conflicts = float(report.get("conflicts", 0.0))
    return round(max(0.0, min(1.0, coverage - 0.10 * conflicts)), 2)


def _build_balanced_owner() -> Owner:
    owner = Owner("Riley", "90")
    pet = Pet("Biscuit", "Dog", "Golden Retriever", 3)
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk", 30, "high", "walk", time_of_day="07:00"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding", time_of_day="08:00"))
    pet.add_task(Task("Medication", 20, "low", "medication", time_of_day="09:00"))
    return owner


def _build_time_limited_owner() -> Owner:
    owner = Owner("Sam", "25")
    pet = Pet("Mochi", "Cat", "Siamese", 2)
    owner.add_pet(pet)
    pet.add_task(Task("Medication", 20, "high", "medication", time_of_day="08:00"))
    pet.add_task(Task("Play", 15, "medium", "general", time_of_day="09:00"))
    return owner


def _build_conflict_owner() -> Owner:
    owner = Owner("Ava", "90")
    pet = Pet("Nori", "Dog", "Corgi", 4)
    owner.add_pet(pet)
    pet.add_task(Task("Walk", 30, "high", "walk", time_of_day="07:00"))
    pet.add_task(Task("Grooming", 20, "medium", "grooming", time_of_day="07:10"))
    return owner


def _build_owner_guidance_owner() -> Owner:
    owner = Owner(
        "Jordan",
        "60",
        preferences={
            "category_guidance": {
                "feeding": "Owner preference: feed after hydration check."
            }
        },
    )
    pet = Pet("Luna", "Dog", "Mixed", 5)
    owner.add_pet(pet)
    pet.add_task(Task("Breakfast", 15, "high", "feeding", time_of_day="08:15"))
    return owner


def _build_specialized_style_owner() -> Owner:
    owner = Owner(
        "Taylor",
        "70",
        preferences={"explanation_style": "clinical_compact"},
    )
    pet = Pet("Pepper", "Cat", "Tabby", 6)
    owner.add_pet(pet)
    pet.add_task(Task("Medication", 10, "high", "medication", time_of_day="07:30"))
    pet.add_task(Task("Feeding", 15, "medium", "feeding", time_of_day="08:00"))
    return owner


def _evaluate_case(case: EvalCase) -> Dict[str, object]:
    owner = case.builder()
    scheduler = Scheduler(owner.available_time)
    scheduler.load_tasks_from_owner(owner)
    plan = scheduler.generate_schedule()
    report = scheduler.reliability_report()
    confidence = _confidence_from_report(report)

    checks: List[str] = []
    failed_checks: List[str] = []

    if case.expected_scheduled is not None:
        scheduled_count = len(plan.scheduled_tasks)
        check_msg = f"scheduled={scheduled_count}, expected={case.expected_scheduled}"
        checks.append(check_msg)
        if scheduled_count != case.expected_scheduled:
            failed_checks.append(check_msg)

    if case.expected_conflicts is not None:
        conflict_count = report["conflicts"]
        check_msg = f"conflicts={conflict_count}, expected={case.expected_conflicts}"
        checks.append(check_msg)
        if conflict_count != case.expected_conflicts:
            failed_checks.append(check_msg)

    if case.expected_contains is not None:
        contains = case.expected_contains in plan.explanation
        check_msg = f"contains='{case.expected_contains}' -> {contains}"
        checks.append(check_msg)
        if not contains:
            failed_checks.append(check_msg)

    passed = len(failed_checks) == 0

    return {
        "name": case.name,
        "status": "PASS" if passed else "FAIL",
        "confidence": confidence,
        "report": report,
        "checks": checks,
        "failed_checks": failed_checks,
    }


def run_evaluation() -> Dict[str, object]:
    cases = [
        EvalCase(
            name="balanced_plan",
            builder=_build_balanced_owner,
            expected_scheduled=3,
            expected_conflicts=0,
            expected_contains="Guidance used:",
        ),
        EvalCase(
            name="time_limited_plan",
            builder=_build_time_limited_owner,
            expected_scheduled=1,
            expected_conflicts=0,
            expected_contains="Skipped due to time:",
        ),
        EvalCase(
            name="conflict_detection",
            builder=_build_conflict_owner,
            expected_scheduled=2,
            expected_conflicts=1,
        ),
        EvalCase(
            name="owner_retrieval_guidance",
            builder=_build_owner_guidance_owner,
            expected_scheduled=1,
            expected_conflicts=0,
            expected_contains="Owner preference: feed after hydration check.",
        ),
        EvalCase(
            name="specialized_style_output",
            builder=_build_specialized_style_owner,
            expected_scheduled=2,
            expected_conflicts=0,
            expected_contains="Care Plan Summary",
        ),
    ]

    results = [_evaluate_case(case) for case in cases]
    pass_count = sum(1 for result in results if result["status"] == "PASS")
    avg_confidence = round(
        sum(float(result["confidence"]) for result in results) / len(results),
        2,
    )

    return {
        "total_cases": len(results),
        "pass_count": pass_count,
        "fail_count": len(results) - pass_count,
        "average_confidence": avg_confidence,
        "results": results,
    }


def print_human_summary(summary: Dict[str, object]) -> None:
    print("PawPal+ Reliability Evaluation")
    print("=" * 32)

    for result in summary["results"]:
        print(
            f"- {result['name']}: {result['status']} | "
            f"confidence={result['confidence']} | "
            f"scheduled={result['report']['scheduled_tasks']} | "
            f"conflicts={result['report']['conflicts']}"
        )
        if result["failed_checks"]:
            print(f"  failed_checks={result['failed_checks']}")

    print("\nSummary")
    print("-" * 32)
    print(f"pass_count: {summary['pass_count']} / {summary['total_cases']}")
    print(f"fail_count: {summary['fail_count']}")
    print(f"average_confidence: {summary['average_confidence']}")


def main() -> None:
    summary = run_evaluation()
    print_human_summary(summary)

    output_path = "logs/reliability_eval_summary_latest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved parseable summary to {output_path}")


if __name__ == "__main__":
    main()
