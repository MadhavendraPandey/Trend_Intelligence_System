import subprocess
import sys
from pathlib import Path

from modules.trend.config import COLLECTOR_MODULES

PROJECT_ROOT = Path(__file__).resolve().parent

COLLECTORS = COLLECTOR_MODULES


def run_collector(module_name):

    print()
    print("=" * 70)
    print(f"Running {module_name}")
    print("=" * 70)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            module_name,
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        print(f"{module_name} failed with exit code {result.returncode}")

    return result.returncode


def run_all_collectors():
    failures = []

    for collector_name in COLLECTORS:
        return_code = run_collector(collector_name)

        if return_code != 0:
            failures.append(collector_name)

    print()
    print("=" * 70)
    print("Collection  complete")
    print("=" * 70)

    if failures:
        print("Failed collectors:")
        for collector_name in failures:
            print(f"- {collector_name}")
        return 1

    print("All collectors completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_all_collectors())
