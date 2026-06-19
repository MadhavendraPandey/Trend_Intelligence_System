# Phase 2 Audit

## Scope

Reviewed:

- `core/storage/sqlite_storage.py`
- `database/repositories/source_repository.py`
- `database/repositories/post_repository.py`
- `database/migrations/001_initial_schema.sql`

No implementation files were modified during this audit.

## Executive Summary

The Phase 1/2 implementation establishes a usable SQLite foundation, but it has several architectural risks that should be corrected before production cutover.

The highest-priority issues are:

1. Migration tracking is not fully reliable because the migration file also creates `schema_migrations`, while `SQLiteStorage` separately creates and writes to the same table.
2. Repository constructors run migrations implicitly, which mixes dependency construction with schema mutation.
3. Repositories are hard-bound to `SQLiteStorage`, making future storage replacement harder than the architecture intends.
4. `posts` currently allows records without durable source identity (`url`, `canonical_url`, `content_hash`, and `source_record_id` are all nullable), which weakens evidence traceability.
5. The schema preserves JSON blobs but lacks constraints/checks for lifecycle and source fields, allowing invalid platform states.

## Architectural Problems

### 1. Repository construction performs schema initialization

Files:

- `database/repositories/source_repository.py:31-36`
- `database/repositories/post_repository.py:44-49`

Both repositories call `storage.initialize()` inside `__init__`.

Problem:

Constructing a repository mutates database state by applying migrations. This makes repository creation side-effectful and blurs lifecycle ownership.

Impact:

- Tests and CLI tools may apply migrations unexpectedly.
- Future read-only contexts cannot safely instantiate repositories.
- Application startup cannot clearly separate "initialize storage" from "use repositories".

Recommendation:

Move migration application to an explicit application/bootstrap step. Repositories should receive an initialized storage object or connection provider.

### 2. Repositories depend on the concrete SQLite implementation

Files:

- `database/repositories/source_repository.py:17,31-33`
- `database/repositories/post_repository.py:20,44-46`

Problem:

Both repositories enforce `isinstance(storage, SQLiteStorage)`.

Impact:

- Violates the replaceability goal.
- Prevents repository tests from using a fake or test storage implementing the same contract.
- Makes future database replacement require repository changes.

Recommendation:

Depend on a narrower storage protocol/interface that exposes connection acquisition, or introduce a `SQLiteRepositoryBase` while keeping the public repository boundary storage-agnostic.

### 3. Storage owns migration execution but not migration policy

File:

- `core/storage/sqlite_storage.py:48-71`

Problem:

`SQLiteStorage.initialize()` applies every `*.sql` file automatically in sorted order with no explicit target version, dry-run mode, lock, checksum, or dirty-state handling.

Impact:

- A partially edited or accidental `.sql` file under `database/migrations` would run automatically.
- No checksum means previously applied migration files can change silently.
- No migration lock means multiple processes may race during startup.

Recommendation:

Add migration metadata with checksum and success status before production use. Consider explicit migration commands separate from ordinary storage health checks.

### 4. Connection lifecycle is shared but not concurrency-aware

File:

- `core/storage/sqlite_storage.py:38-46`

Problem:

`SQLiteStorage` maintains one persistent connection and shares it with repositories.

Impact:

- This is fine for single-threaded local use, but unsafe for future concurrent collectors or background jobs without a connection policy.
- No timeout, isolation mode, WAL mode, or busy timeout is configured.

Recommendation:

Document single-process/single-writer assumptions now. Before concurrent collection, configure `PRAGMA busy_timeout`, consider WAL, and decide whether repositories get per-operation connections.

## Schema Problems

### 1. `schema_migrations` is created in two places

Files:

- `core/storage/sqlite_storage.py:94-104`
- `database/migrations/001_initial_schema.sql:8-12`

Problem:

The storage layer creates `schema_migrations` before applying migrations, and the initial migration also creates it.

Impact:

- Not currently fatal because both definitions match, but it creates ownership ambiguity.
- Future changes to `schema_migrations` could diverge between Python and SQL.

Recommendation:

Choose one owner. Prefer a tiny bootstrap table owned by storage, and remove `schema_migrations` from ordinary migrations in the next schema revision, or keep all schema definition in migrations and make storage bootstrap minimal and identical by contract.

### 2. Phase 1 migration is not fully idempotent with migration bookkeeping

Files:

- `core/storage/sqlite_storage.py:61-69`
- `database/migrations/001_initial_schema.sql:8-94`

Problem:

The migration body uses `CREATE TABLE IF NOT EXISTS`, while migration application records the migration version after execution. If execution partly succeeds and fails later, rerun behavior may be ambiguous.

Impact:

- A partial schema can exist without a migration row.
- Re-running may hide partial-application problems because `IF NOT EXISTS` suppresses errors.

Recommendation:

For production migrations, avoid using `IF NOT EXISTS` for versioned schema objects except for carefully managed bootstrap objects. Let migration failures fail loudly.

### 3. `posts` permits weak identity

File:

- `database/migrations/001_initial_schema.sql:52-77`

Problem:

`url`, `canonical_url`, `source_record_id`, and `content_hash` are all nullable.

Impact:

- The platform can store posts that cannot be reliably deduplicated or traced back to a source record.
- This weakens evidence-first traceability.

Recommendation:

Add an explicit identity policy before cutover. At least one durable identifier should be required: `canonical_url`, `url`, `source_record_id`, or `content_hash`.

### 4. Redundant source type storage can drift

Files:

- `database/migrations/001_initial_schema.sql:16`
- `database/migrations/001_initial_schema.sql:56`

Problem:

`source_type` exists in both `sources` and `posts`.

Impact:

- A post can reference a `sources` row with source type `rss` while storing post `source_type = github`.
- This creates inconsistent lineage.

Recommendation:

Either derive post source type through `source_id`, or enforce consistency in repository code. If denormalized for query speed, document it and validate it.

### 5. No check constraints for lifecycle fields

Files:

- `database/migrations/001_initial_schema.sql:19-20`
- `database/migrations/001_initial_schema.sql:34`

Problem:

Fields such as `owner_module`, `is_active`, and `status` accept arbitrary values.

Impact:

- Invalid states can enter the database.
- Future reports may need defensive cleanup logic.

Recommendation:

Add `CHECK` constraints or central constants for allowed values. For `is_active`, constrain to `0` or `1`.

### 6. Source run counters are operational metrics without integrity checks

File:

- `database/migrations/001_initial_schema.sql:35-38`

Problem:

`items_seen`, `items_stored`, `duplicates_seen`, and `errors_seen` are integers but can be negative.

Impact:

- Operational audit data can become nonsensical.

Recommendation:

Add non-negative `CHECK` constraints before relying on source run metrics.

### 7. `updated_at` does not update automatically

Files:

- `database/migrations/001_initial_schema.sql:22`
- `database/migrations/001_initial_schema.sql:70`

Problem:

The schema defines `updated_at`, but SQLite does not auto-update it. Current repositories manually update it for `sources` and `posts`, but future SQL paths could miss it.

Impact:

- Timestamp consistency depends on every repository method remembering to update it.

Recommendation:

Either keep repository-managed timestamps as a documented rule or add triggers.

## Repository Design Problems

### 1. Update methods silently ignore invalid fields

Files:

- `database/repositories/source_repository.py:81-90`
- `database/repositories/post_repository.py:127-136`

Problem:

Unknown update fields are silently dropped.

Impact:

- Caller mistakes can appear successful while doing nothing.
- API misuse becomes hard to detect.

Recommendation:

Raise a clear error for unknown fields, or return structured information about ignored fields.

### 2. Update methods do not report missing records

Files:

- `database/repositories/source_repository.py:97-106`
- `database/repositories/post_repository.py:143-152`

Problem:

Updating a missing id returns `None` after executing an update.

Impact:

- Callers cannot easily distinguish "record missing" from "record updated to no visible change" unless they check return value.

Recommendation:

Raise a repository-level not-found error or return an explicit result object.

### 3. Pagination inputs are not validated

Files:

- `database/repositories/source_repository.py:108-137`
- `database/repositories/post_repository.py:169-205`

Problem:

`limit` and `offset` are passed directly as query parameters without validation.

Impact:

- Negative or huge values can create confusing behavior or accidental large scans.

Recommendation:

Validate `limit >= 1`, cap maximum limit, and require `offset >= 0`.

### 4. JSON fields are serialized inconsistently

File:

- `database/repositories/post_repository.py:207-211`

Problem:

`_json_or_text` serializes dict/list values but passes strings through unchanged.

Impact:

- `raw_json` and `metadata_json` may contain valid JSON, arbitrary text, or invalid JSON depending on caller.
- Future migrations and exports will need defensive parsing.

Recommendation:

Use explicit `raw` and `metadata` parameters that always serialize to JSON, or validate string inputs as JSON.

### 5. `get_by_url` does not normalize URL identity

File:

- `database/repositories/post_repository.py:154-167`

Problem:

`get_by_url` performs exact matching against `url` and `canonical_url`.

Impact:

- Dedupe remains fragile across trailing slashes, tracking params, casing, HTTP/HTTPS variants, and canonicalization differences.

Recommendation:

Keep canonicalization out of repository business logic, but require callers to provide `canonical_url` and document exact-match semantics.

### 6. Repository SQL is manually duplicated and untyped

Files:

- `database/repositories/source_repository.py`
- `database/repositories/post_repository.py`

Problem:

Repositories return raw dicts without typed objects or row schemas.

Impact:

- Callers must know exact database field names.
- Future schema refactors will leak into modules unless repository return contracts are stabilized.

Recommendation:

Introduce lightweight dataclasses or schema objects after Phase 2, especially for `Post` and `Source`.

## Future Migration Risks

### 1. Existing JSON data does not map cleanly to the Phase 1 schema

Current JSON article objects contain fields like:

- `filter_data`
- `analysis`
- `source_quality_score`
- `trend_score`
- `opportunity_score`
- source-specific `metadata`

Problem:

Phase 1 `posts` has `raw_json` and `metadata_json`, but no explicit home for legacy analysis/filter fields.

Risk:

Without a clear migration policy, important historical data may be buried in `raw_json` and become difficult to query.

Recommendation:

Before JSON migration, define exactly which legacy fields become canonical post fields, which remain in `raw_json`, and which become generated report artifacts.

### 2. Canonical post identity is unresolved

Risk:

Different sources identify posts differently: RSS URLs, GitHub repo URLs, Hacker News item IDs, arXiv IDs, Reddit permalinks, comments, and future forum posts.

Recommendation:

Define source-specific canonical identity rules before import. The database should not rely only on caller discipline.

### 3. Future evidence tables will need strong linkage to current posts

Risk:

If weak post identity enters now, future evidence links may point to duplicate or poorly traced posts.

Recommendation:

Harden post identity before implementing evidence tables.

### 4. Migration file mutability is not guarded

Risk:

Changing `001_initial_schema.sql` after real databases exist could create environments with the same migration version and different schema.

Recommendation:

Add migration checksums or an explicit "do not edit applied migrations" policy before production use.

### 5. Existing reports still read JSON directly

Risk:

SQLite may be "primary architecture" while operational behavior remains JSON-based for a long time.

Recommendation:

Plan a repository-backed read path for reports after JSON import/export policy is settled.

## Evidence-First Philosophy Violations

### 1. Weak source traceability is allowed

File:

- `database/migrations/001_initial_schema.sql:52-77`

Why it matters:

Evidence-first systems must preserve where observations came from. Because `posts` can be inserted with no URL, no canonical URL, no source record id, and no content hash, some observations may not be traceable enough for later validation.

### 2. Operational source counters could become untrustworthy

File:

- `database/migrations/001_initial_schema.sql:35-38`

Why it matters:

Evidence-first systems rely on auditability. Negative or unconstrained source-run counters weaken trust in collection history.

### 3. Raw JSON is preserved, but not governed

Files:

- `database/migrations/001_initial_schema.sql:67-68`
- `database/repositories/post_repository.py:207-211`

Why it matters:

Raw JSON preservation supports traceability, but without validation or a migration policy it can become an opaque dumping ground. Evidence-first architecture needs raw material plus clear contracts for what has been normalized.

### 4. Repository return contracts expose storage shape directly

Files:

- `database/repositories/source_repository.py:139-143`
- `database/repositories/post_repository.py:213-217`

Why it matters:

Evidence-first objects should be stable language for future developers and agents. Returning raw table dicts couples callers to storage columns instead of platform concepts.

## Recommended Remediation Order

1. Decide migration ownership for `schema_migrations` and remove duplicate ownership.
2. Separate storage initialization/migration application from repository construction.
3. Replace concrete `SQLiteStorage` type checks with an interface/protocol.
4. Add post identity policy before JSON migration.
5. Add constraints for boolean, status, and non-negative counter fields.
6. Validate pagination and unknown update fields in repositories.
7. Define JSON field governance for `raw_json` and `metadata_json`.
8. Introduce stable row/domain return contracts before modules consume repositories broadly.

