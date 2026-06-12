import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_command(command):
    print()
    print("=" * 70)
    print("Running: " + " ".join(command))
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    return result.returncode


def run_daily_pipeline():
    failures = []
    commands = [
        [sys.executable, "main_collector.py"],
        [sys.executable, "analyzer.py"],
        [sys.executable, "reporter.py"],
    ]

    for command in commands:
        return_code = run_command(command)

        if return_code != 0:
            failures.append(command)

    return failures


def run_weekly_brief():
    return run_command(
        [
            sys.executable,
            "reports/weekly_brief.py",
        ]
    )


def main():
    failures = run_daily_pipeline()

    if datetime.now().weekday() == 0:
        weekly_return_code = run_weekly_brief()

        if weekly_return_code != 0:
            failures.append(["reports/weekly_brief.py"])

    print()
    print("=" * 70)
    print("Scheduler complete")
    print("=" * 70)

    if failures:
        print("Failed jobs:")
        for command in failures:
            print("- " + " ".join(command))
        return 1

    print("All scheduled jobs completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
