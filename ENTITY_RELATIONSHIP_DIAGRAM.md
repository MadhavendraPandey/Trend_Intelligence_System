# Entity Relationship Diagram

## Evidence-First Relationship Diagram

```mermaid
erDiagram
    SOURCES ||--o{ SOURCE_RUNS : records
    SOURCES ||--o{ POSTS : emits
    SOURCE_RUNS ||--o{ POSTS : captures

    POSTS ||--o{ EVIDENCE : provides
    POSTS ||--o{ POST_ENTITIES : mentions
    ENTITIES ||--o{ POST_ENTITIES : appears_in

    POSTS ||--o{ POST_TOPICS : has
    TOPICS ||--o{ POST_TOPICS : labels

    TOPICS ||--o{ TRENDS : organizes
    TRENDS ||--o{ TREND_OBSERVATIONS : contains
    POSTS ||--o{ TREND_OBSERVATIONS : supports
    TOPICS ||--o{ TREND_OBSERVATIONS : contextualizes
    TRENDS ||--o{ TREND_EVIDENCE : supported_by
    EVIDENCE ||--o{ TREND_EVIDENCE : supports

    POSTS ||--o{ COMPLAINTS : contains
    COMPLAINTS ||--o{ COMPLAINT_SIGNALS : has
    COMPLAINTS ||--o{ COMPLAINT_EVIDENCE : supported_by
    EVIDENCE ||--o{ COMPLAINT_EVIDENCE : supports

    FRICTION_CANDIDATES ||--o{ FRICTION_CANDIDATE_COMPLAINTS : groups
    COMPLAINTS ||--o{ FRICTION_CANDIDATE_COMPLAINTS : belongs_to
    FRICTION_CANDIDATES ||--o{ FRICTION_CANDIDATE_EVIDENCE : supported_by
    EVIDENCE ||--o{ FRICTION_CANDIDATE_EVIDENCE : supports

    FRICTION_CANDIDATES ||--o{ FRICTIONS : promoted_to
    FRICTIONS ||--o{ FRICTION_EVIDENCE : supported_by
    EVIDENCE ||--o{ FRICTION_EVIDENCE : supports
    FRICTIONS ||--o{ FRICTION_WORKAROUNDS : has
    POSTS ||--o{ FRICTION_WORKAROUNDS : observes
    EVIDENCE ||--o{ FRICTION_WORKAROUNDS : documents

    TRENDS ||--o{ VALIDATION_EVENTS : reviewed_by
    FRICTIONS ||--o{ VALIDATION_EVENTS : reviewed_by
    FRICTION_CANDIDATES ||--o{ VALIDATION_EVENTS : reviewed_by
    COMPLAINTS ||--o{ VALIDATION_EVENTS : reviewed_by
```

## Relationship Notes

- `posts` are the canonical normalized observation unit.
- `evidence` records traceable excerpts, links, notes, or source artifacts.
- `trends` are supported by repeated observations and linked evidence.
- `complaints` are atomic problem observations connected to posts and evidence.
- `friction_candidates` group complaints before human validation.
- `frictions` represent human-validated persistent friction patterns.
- `validation_events` preserve human decisions as event history instead of storing confidence scores.

## Dependency Direction

Database access should remain behind repositories:

```text
modules / reports
        ↓
repositories
        ↓
core storage
        ↓
SQLite
```

Engines and reports should not execute raw SQL or manage SQLite connections directly.
