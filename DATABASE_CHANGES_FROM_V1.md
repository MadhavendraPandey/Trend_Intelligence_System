# Database Changes From V1

## Removed Fields

The V2 architecture removes score-based and judgment-like fields from canonical storage:

- `confidence`
- `signal_strength`
- `trend_score`
- `candidate_score`
- `friction_score`
- `opportunity_score`
- `rank`
- `trend_level`
- `opportunity_level`
- `severity` as a numeric judgment field

These values may still appear in legacy runtime reports while the existing Trend Intelligence pipeline is preserved, but they should not become canonical SQLite truth.

## Added Fields

The V2 architecture adds observable fields:

- `first_seen`
- `last_seen`
- `supporting_post_count`
- `evidence_count`
- `complaint_count`
- `source_count`
- `validation_count`
- `workaround_count`
- `observed_at`
- `validation_state`
- `relationship_type`
- `captured_at`
- `published_at`
- `context`

These fields describe what was observed, when it was observed, where it came from, and how it relates to other observations.

## Modified Tables

### `trend_signals` -> `trend_observations`

`trend_signals` implied score-based signal strength. V2 uses `trend_observations` to represent concrete post-level observations that support a trend.

### `trends`

`trends` becomes an evidence grouping table, not a ranked output table.

Removed concepts:
- trend score
- trend level
- confidence
- rank

Added concepts:
- first seen
- last seen
- source count
- supporting post count
- evidence count
- active window
- lifecycle status

### `friction_candidates`

`friction_candidates` stores counts and lifecycle state, not candidate score.

Added concepts:
- complaint count
- supporting post count
- evidence count
- workaround count
- first seen
- last seen
- lifecycle status

### `frictions`

`frictions` stores validation state and evidence counts, not final judgment scores.

Added concepts:
- validation state
- validation count
- supporting complaint count
- supporting post count
- evidence count
- first seen
- last seen

### `evidence`

`evidence` becomes a first-class traceability object with source, quote, context, and timestamps.

It can support multiple target types through explicit join tables:
- trends
- complaints
- friction candidates
- validated frictions

### `validation_events`

`validation_events` replaces confidence and AI certainty.

The database records human validation actions as durable events instead of compressing judgment into numeric fields.

## Reasoning

The V1 proposal mixed observations with platform judgments. V2 records what was seen, where it was seen, how often it recurs, what evidence supports it, and what humans validated.

Any ranking or scoring can still be computed transiently in reports, but it should not become canonical platform truth.
