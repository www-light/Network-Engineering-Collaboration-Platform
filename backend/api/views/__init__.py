"""Views module - organize all API view functions"""

from .health import health_check
from .auth import register, login
from .post import like, favorite, comment
from .conversation import (
    create_conversation,
    list_conversations,
    close_conversation,
    send_message,
    list_messages
)
from .tag import tags
from .project import publish_project, list_projects

__all__ = [
    'health_check',
    'register',
    'login',
    'like',
    'favorite',
    'comment',
    'create_conversation',
    'list_conversations',
    'close_conversation',
    'send_message',
    'list_messages',
    'tags',
    'publish_project',
    'list_projects',
]
