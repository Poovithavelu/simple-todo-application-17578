"""
PUBLIC_INTERFACE
Routes package initializer.

This module exposes blueprints for import in the application factory.
"""
from .health import blp as health_blp  # Health check blueprint
from .todos import blp as todos_blp    # Todos CRUD blueprint

__all__ = ["health_blp", "todos_blp"]
