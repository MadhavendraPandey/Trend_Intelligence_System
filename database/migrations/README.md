# Database Migrations

Purpose:
This directory contains ordered SQL migrations for the Intelligence Platform
SQLite database.

Architecture notes:
Migrations are applied by `core.storage.SQLiteStorage`. Phase 1 creates only
the foundational source tracking and post tables.

Future extension guidance:
Add future migrations with numeric prefixes, for example
`002_evidence_tables.sql`. Do not edit already-applied migrations after they
are used by a real database.
