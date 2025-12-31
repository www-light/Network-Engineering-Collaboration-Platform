"""Views module - organize all API view functions"""

from .health import health_check
from .auth import register, login
from .post import like, unlike, favorite, unfavorite, comment, list_comments
from .conversation import (
    create_conversation,
    list_conversations,
    close_conversation,
    send_message,
    list_messages
)
from .tag import tags
from .project import list_projects, get_project_detail, publish_research, publish_competition, publish_personal

__all__ = [
    'health_check',
    'register',
    'login',
    'like',
    'unlike',
    'favorite',
    'unfavorite',
    'comment',
    'list_comments',
    'create_conversation',
    'list_conversations',
    'close_conversation',
    'send_message',
    'list_messages',
    'tags',
    'list_projects',
    'get_project_detail',
    'publish_research',
    'publish_competition',
    'publish_personal',
]
