# Static Assets

Purpose:
This directory stores workbench-owned static media such as icons, screenshots,
or small product assets.

Architecture notes:
Assets here are presentation concerns only. They must not contain intelligence
data exports, database backups, or generated reports.

Future extension guidance:
Keep assets lightweight and reference them through the FastAPI static mount.
