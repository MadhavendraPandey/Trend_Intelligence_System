"""FastAPI compatibility exports for the Intelligence Workbench.

Purpose:
    Prefer the real FastAPI package while keeping the dashboard importable in
    lightweight local environments that only have Starlette available.

Architecture notes:
    This module intentionally lives under `website.compat` so the repository no
    longer shadows the third-party `fastapi` package name. The fallback supports
    only the subset used by the server-rendered, read-only workbench: GET
    routes, path/query parameter binding, HTTP exceptions, static files, Jinja
    templates, HTML responses, and test clients.

Future extension guidance:
    Add the real FastAPI dependency for production deployments. Keep this
    fallback small and remove it once the environment dependency is explicit.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

try:  # pragma: no cover - exercised only when FastAPI is installed.
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, Response
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover - fallback is validated by smoke tests.
    from starlette.applications import Starlette
    from starlette.exceptions import HTTPException
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, Response
    from starlette.routing import Route
    from starlette.staticfiles import StaticFiles
    from starlette.templating import Jinja2Templates
    from starlette.testclient import TestClient

    class FastAPI(Starlette):
        """Small FastAPI-like facade backed by Starlette."""

        def __init__(self, title=None, version=None, **kwargs):
            super().__init__(**kwargs)
            self.title = title
            self.version = version

        def get(self, path: str, response_class: type[Response] = Response):
            """Register a GET endpoint using FastAPI-style decorator syntax."""

            def decorator(func: Callable[..., Any]):
                async def endpoint(request: Request):
                    kwargs = {}
                    signature = inspect.signature(func)

                    for name, parameter in signature.parameters.items():
                        if name == "request":
                            kwargs[name] = request
                            continue

                        if name in request.path_params:
                            raw_value = request.path_params[name]
                        elif name in request.query_params:
                            raw_value = request.query_params[name]
                        elif parameter.default is not inspect._empty:
                            raw_value = parameter.default
                        else:
                            raw_value = None

                        annotation = parameter.annotation
                        if annotation in (int, "int") and raw_value is not None:
                            try:
                                raw_value = int(raw_value)
                            except (TypeError, ValueError) as exc:
                                raise HTTPException(
                                    status_code=422,
                                    detail=f"Invalid integer parameter: {name}",
                                ) from exc

                        kwargs[name] = raw_value

                    result = func(**kwargs)
                    if hasattr(result, "__await__"):
                        result = await result

                    if isinstance(result, Response):
                        return result

                    if response_class is HTMLResponse:
                        return HTMLResponse(result)

                    return response_class(result)

                route = Route(path, endpoint=endpoint, methods=["GET"])
                self.router.routes.append(route)
                return func

            return decorator

__all__ = [
    "FastAPI",
    "HTTPException",
    "HTMLResponse",
    "Jinja2Templates",
    "Request",
    "Response",
    "StaticFiles",
    "TestClient",
]
