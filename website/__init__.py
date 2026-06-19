"""Website package for the read-only Intelligence Workbench.

Purpose:
    Own the server-rendered FastAPI/Jinja inspection interface for posts,
    evidence, evidence groups, candidate frictions, and operational run data.

Architecture notes:
    The website is read-only and repository-driven. Import the ASGI application
    from `website.app` when starting the server.

Future extension guidance:
    Add routes, services, templates, and static assets here without moving
    intelligence logic into the web layer.
"""
