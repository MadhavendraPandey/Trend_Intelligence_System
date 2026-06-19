# Database Philosophy Alignment

## Evidence First

The schema begins with `posts` and `evidence`. Trends, complaints, candidates, and frictions are all supported through explicit observation and evidence join tables.

Every durable intelligence object can answer:

> What evidence supports this?

Evidence is not an annotation on the side of the system. It is a first-class object with source, quote, context, author, source URL, captured time, and published time.

## Human Judgment Over AI Judgment

The schema removes confidence and score fields from canonical tables. Validation is represented by `validation_events`, where humans record decisions, rationale, and event history.

The database records that a person validated, rejected, reopened, merged, split, or archived something. It does not pretend certainty.

Runtime or report-era ranking may still exist for compatibility, but those outputs are generated artifacts rather than canonical database truth.

## Traceability

`source_runs`, `posts`, `evidence`, and validation snapshots preserve collection lineage.

Traceability is supported by storing:
- source identity
- source run
- source URL
- author
- captured timestamp
- published timestamp
- raw JSON
- evidence quote
- surrounding context
- relationships between evidence and higher-level objects

This allows a future reviewer to trace a trend or friction back to original material.

## Validation

Validation is event-based. Trends and frictions can be observed for long periods before being validated.

`validation_events` supports multiple human actions over time:
- validated
- rejected
- needs_more_evidence
- merged
- split
- archived
- reopened

This preserves the history of human judgment instead of collapsing it into a score.

## Persistence

Persistence is represented by observable fields:
- `first_seen`
- `last_seen`
- `supporting_post_count`
- `evidence_count`
- `complaint_count`
- `source_count`
- `validation_count`
- `workaround_count`

No persistence score is stored. Persistence is something a human can inspect from repeated observations over time and across sources.

## What The Database Does Not Store

The canonical database does not store:
- confidence scores
- opportunity scores
- trend scores
- friction scores
- signal strength
- AI certainty
- final recommendations as truth

Generated reports may contain derived interpretations for compatibility, but those reports should be stored as snapshots, not as canonical evidence.
