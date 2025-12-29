"""Views module - organize all API view functions"""

from .health import health_check
from .auth import register, login

__all__ = [
    'health_check',
    'register',
    'login',
]
