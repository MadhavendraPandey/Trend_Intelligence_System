"""Compatibility helpers for the website package.

Purpose:
    Keep optional web-framework compatibility inside the website boundary.

Architecture notes:
    The application prefers the real FastAPI package. When that dependency is
    not installed in a local development environment, website.compat.fastapi
    provides the small server-side rendering subset needed by the read-only
    workbench.

Future extension guidance:
    Do not add intelligence logic here. Compatibility modules should stay
    focused on framework adaptation.
"""

