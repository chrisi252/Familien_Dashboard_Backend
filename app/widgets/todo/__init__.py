from .widget import TodoWidget
from app.widgets.registry import register

register(TodoWidget())

__all__ = ['TodoWidget']
