import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.planner import PlannerAgent


def main() -> None:
    planner = PlannerAgent()
    questions = [
        "Explain Marketing Mart",
        "What is Bread Financial?",
        "Show workflow of Billing Data Mart",
        "Explain mapping document columns",
    ]

    for question in questions:
        print("----------------------------------------")
        print("Question:")
        print(question)
        print("Planning Result:")
        print(planner.plan(question))
        print("----------------------------------------")


if __name__ == "__main__":
    main()
