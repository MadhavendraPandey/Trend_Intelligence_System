# Friction Runner Report

## Scope

Implemented the friction pipeline orchestration layer only.

Pipeline:

```text
Posts
  -> LLM Evidence Extraction
  -> Evidence
  -> LLM Evidence Grouping
  -> Evidence Groups
  -> Candidate Frictions
```

## Files Modified

- `modules/friction/runner.py`

## Files Created

- `FRICTION_RUNNER_REPORT.md`

## Runner Responsibilities

The runner:

- initializes repositories
- initializes an LLM provider
- runs evidence extraction
- runs evidence grouping
- runs candidate generation
- supports dry-run mode
- supports `--limit`
- supports logging via console output
- prints a run summary

## CLI

```bash
python -m modules.friction.runner --limit 100 --provider qwen --model qwen2.5:3b
```

Options:

- `--limit`
- `--dry-run`
- `--provider`
- `--model`

## Explicitly Not Implemented

- validated frictions
- opportunity detection
- reports
- scoring
- ranking

## Validation Results

Passed.

Checks run:

- Compile:
  - `.venv\Scripts\python.exe -m compileall modules\friction core database main.py scheduler.py`
  - Result: passed
- Repository integration:
  - Created a temporary SQLite database.
  - Created a source and post through repositories.
  - Ran the runner against the repository-backed data with a fake provider.
  - Result: passed
- Dry-run execution:
  - Verified `--dry-run` path returned a summary without writing evidence,
    evidence groups, or candidate frictions.
  - Result: passed
- Temporary SQLite validation:
  - Verified the runner can execute end-to-end orchestration against a
    temporary SQLite database.
  - Verified evidence extraction, evidence grouping, and candidate generation
    all integrated through existing services.
  - Result: passed

Notes:

- Validation used a temporary SQLite database and fake LLM provider.
- No validated frictions, opportunity detection, reports, scoring, or ranking
  was added or executed.
