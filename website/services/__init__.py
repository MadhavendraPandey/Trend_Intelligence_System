"""Service layer for the read-only Intelligence Workbench.

Purpose:
    Convert repository reads into template-friendly view data.

Architecture notes:
    Services may coordinate repositories but must not perform intelligence
    generation, scoring, extraction, grouping, or candidate creation.

Future extension guidance:
    Add narrowly scoped read services as pages grow more complex.
"""

