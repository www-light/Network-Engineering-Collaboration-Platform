"""Views module - organize all API view functions"""

from .health import health_check
from .auth import register, login
from .post import like, favorite, comment

__all__ = [
    'health_check',
    'register',
    'login',
    'like',
    'favorite',
    'comment',
]
