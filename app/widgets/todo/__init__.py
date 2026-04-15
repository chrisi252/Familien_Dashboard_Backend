from app.widgets.registry import register

from .widget import TodoWidget

register(TodoWidget())

__all__ = ['TodoWidget']
