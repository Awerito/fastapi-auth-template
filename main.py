"""Entry point for the FastAPI CLI."""

# The FastAPI CLI expects an ``app`` variable that references the ``FastAPI``
# application. With this file in place the application can be started with:
# ``fastapi dev main:app`` or ``fastapi run main:app``.

from app.main import app

__all__ = ["app"]
