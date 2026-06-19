"""Database package for Intelligence Platform persistence.

Purpose:
    Hold database migrations and repository boundaries for platform storage.

Architecture notes:
    SQL migrations live under database/migrations. Repository classes will
    live under database/repositories and should be the only application layer
    that issues domain-specific database queries.

Future extension guidance:
    Add new migrations incrementally. Do not let intelligence modules bypass
    repositories to execute raw SQL.
"""
