import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

COMMANDS = {
    "collect": "main_collector.py",
    "analyze": "analyzer.py",
    "report": "reporter.py",
}

FULL_SEQUENCE = [
    "collect",
    "analyze",
    "report",
]


def print_separator():
    print("=" * 70)


def run_script(mode):
    script_name = COMMANDS[mode]
    script_path = PROJECT_ROOT / script_name

    print()
    print_separator()
    print(f"Starting {mode}: {script_name}")
    print_separator()

    if not script_path.exists():
        print(f"Missing script: {script_path}")
        return 1

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
            ],
            cwd=PROJECT_ROOT,
            check=False,
        )

    except KeyboardInterrupt:
        print(f"\nInterrupted while running {mode}.")
        return 130

    except Exception as error:
        print(f"{mode} failed before starting: {error}")
        return 1

    if result.returncode != 0:
        print(f"{mode} failed with exit code {result.returncode}")
    else:
        print(f"{mode} completed successfully")

    return result.returncode


def run_mode(mode):
    if mode == "full":
        failures = []

        for step in FULL_SEQUENCE:
            return_code = run_script(step)

            if return_code != 0:
                failures.append((step, return_code))
                break

        return failures

    return_code = run_script(mode)

    if return_code != 0:
        return [(mode, return_code)]

    return []


def parse_args():
    parser = argparse.ArgumentParser(
        description="Trend Intelligence System entry point"
    )
    parser.add_argument(
        "mode",
        choices=[
            "collect",
            "analyze",
            "report",
            "full",
        ],
        help="Pipeline mode to run",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    start_time = time.perf_counter()

    print_separator()
    print("TREND INTELLIGENCE SYSTEM")
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
        for mode, return_code in failures:
            print(f"- {mode}: exit code {return_code}")
        return 1

    print("Status: SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
