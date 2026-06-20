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
from typing import Any, Callable, List

try:  # pragma: no cover - exercised only when FastAPI is installed.
    from fastapi import APIRouter, FastAPI, HTTPException, Request, Depends, Form
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

    def Form(default: Any = None):
        """Small Form facade."""
        class FormField:
            def __init__(self, default):
                self.default = default
        return FormField(default)

    class APIRouter:
        """Small APIRouter-like facade."""

        def __init__(self):
            self.routes = []

        def get(self, path: str, response_class: type[Response] = Response):
            """Register a GET endpoint using FastAPI-style decorator syntax."""

            def decorator(func: Callable[..., Any]):
                async def endpoint(request: Request, **kwargs):
                    # In the fallback, the decorator handles the call
                    return await self._call_endpoint(func, request, response_class, **kwargs)

                # Store the intent to register this route
                self.routes.append((path, func, response_class, ["GET"]))
                return func

            return decorator

        def post(self, path: str, response_class: type[Response] = Response):
            """Register a POST endpoint using FastAPI-style decorator syntax."""

            def decorator(func: Callable[..., Any]):
                async def endpoint(request: Request, **kwargs):
                    return await self._call_endpoint(func, request, response_class, **kwargs)

                self.routes.append((path, func, response_class, ["POST"]))
                return func

            return decorator

        async def _call_endpoint(self, func, request, response_class, **kwargs):
            # Resolve dependencies and parameters
            call_kwargs = {}
            signature = inspect.signature(func)

            for name, parameter in signature.parameters.items():
                if name == "request":
                    call_kwargs[name] = request
                    continue

                # Handle Depends (very basic fallback)
                if hasattr(parameter.default, "dependency") or "Depends" in str(parameter.default):
                    # We just call the dependency if it's reachable or ignore if it's get_repositories
                    # In our case we know it's get_repositories
                    from website.services.repository_provider import get_repositories
                    call_kwargs[name] = get_repositories(request)
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

                call_kwargs[name] = raw_value

            result = func(**call_kwargs)
            if hasattr(result, "__await__"):
                result = await result

            if isinstance(result, Response):
                return result

            if response_class is HTMLResponse:
                return HTMLResponse(result)

            return response_class(result)

    class FastAPI(Starlette):
        """Small FastAPI-like facade backed by Starlette."""

        def __init__(self, title=None, version=None, **kwargs):
            super().__init__(**kwargs)
            self.title = title
            self.version = version

        def include_router(self, router: APIRouter):
            """Register all routes from a router."""
            for path, func, response_class, methods in router.routes:
                if "POST" in methods:
                    self.post(path, response_class)(func)
                else:
                    self.get(path, response_class)(func)

        def get(self, path: str, response_class: type[Response] = Response):
            """Register a GET endpoint using FastAPI-style decorator syntax."""

            def decorator(func: Callable[..., Any]):
                async def endpoint(request: Request):
                    return await self._call_endpoint(func, request, response_class)

                route = Route(path, endpoint=endpoint, methods=["GET"])
                self.router.routes.append(route)
                return func

            return decorator

        def post(self, path: str, response_class: type[Response] = Response):
            """Register a POST endpoint using FastAPI-style decorator syntax."""

            def decorator(func: Callable[..., Any]):
                async def endpoint(request: Request):
                    return await self._call_endpoint(func, request, response_class)

                route = Route(path, endpoint=endpoint, methods=["POST"])
                self.router.routes.append(route)
                return func

            return decorator

        async def _call_endpoint(self, func, request, response_class):
            kwargs = {}
            signature = inspect.signature(func)
            form_data = None

            for name, parameter in signature.parameters.items():
                if name == "request":
                    kwargs[name] = request
                    continue

                # Handle Form data
                if "FormField" in str(parameter.default):
                    if form_data is None:
                        form_data = await request.form()
                    kwargs[name] = form_data.get(name)
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

def Depends(dependency: Callable[..., Any] = None):
    """Small Depends facade."""
    class Dependency:
        def __init__(self, dep):
            self.dependency = dep
    return Dependency(dependency)

__all__ = [
    "APIRouter",
    "Depends",
        "Form",
    "FastAPI",
    "HTTPException",
    "HTMLResponse",
    "Jinja2Templates",
    "Request",
    "Response",
    "StaticFiles",
    "TestClient",
]
