"""Root entry point for the Intelligence Platform.

Sequences the trend pipeline (collect -> analyze -> report) and the friction
pipeline (extraction -> grouping -> candidates -> validation -> profiles ->
report) from a single command. Each module still owns its own runner; this
script only decides the order they run in.
"""

import argparse
import subprocess
import sys
import time

from modules.trend.config import FULL_SEQUENCE as TREND_SEQUENCE, PROJECT_ROOT
from modules.trend.runner import print_separator, run_script

FRICTION_STEP = "friction"
FULL_SEQUENCE = list(TREND_SEQUENCE) + [FRICTION_STEP]


def run_friction_step():
    print()
    print_separator()
    print(f"Starting {FRICTION_STEP}: modules.friction.runner")
    print_separator()

    result = subprocess.run(
        [sys.executable, "-m", "modules.friction.runner"],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode != 0:
        print(f"{FRICTION_STEP} failed with exit code {result.returncode}")
    else:
        print(f"{FRICTION_STEP} completed successfully")

    return result.returncode


def run_step(step):
    if step == FRICTION_STEP:
        return run_friction_step()

    return run_script(step)


def run_mode(mode):
    sequence = FULL_SEQUENCE if mode == "full" else [mode]
    failures = []

    for step in sequence:
        return_code = run_step(step)

        if return_code != 0:
            failures.append((step, return_code))

            if mode == "full":
                break

    return failures


def parse_args():
    parser = argparse.ArgumentParser(
        description="Intelligence Platform entry point"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=[
            "collect",
            "analyze",
            "report",
            "friction",
            "full",
        ],
        help="Pipeline mode to run",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    start_time = time.perf_counter()

    print_separator()
    print("INTELLIGENCE PLATFORM")
    print_separator()
    print(f"Mode: {args.mode}")

    failures = run_mode(args.mode)
    elapsed_seconds = time.perf_counter() - start_time

    print()
    print_separator()
    print("Run Summary")
    print_separator()
    print(f"Execution Time: {elapsed_seconds:.2f} seconds")

    if failures:
        print("Status: FAILED")
        for step, return_code in failures:
            print(f"- {step}: exit code {return_code}")
        return 1

    print("Status: SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
