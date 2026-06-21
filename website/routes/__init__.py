"""Route modules for the Intelligence Workbench.

Purpose:
    Keep HTTP route registration separated by workbench section.

Architecture notes:
    Route functions should assemble view-models through website services and
    render templates. They should not execute SQL or run intelligence logic.

Future extension guidance:
    Add a new route module for each major navigation section as it becomes
    real product surface.
"""

