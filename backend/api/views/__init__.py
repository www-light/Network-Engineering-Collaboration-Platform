"""Views module - organize all API view functions"""

from .health import health_check
from .auth import register, login, user_profile
from .post import like, unlike, favorite, unfavorite, comment, list_comments
from .attachment import upload_attachment, download_attachment
from .conversation import (
    create_conversation,
    list_conversations,
    close_conversation,
    send_message,
    list_messages,
    auto_reply_settings
)
from .tag import tags
from .project import list_projects, get_project_detail, update_recruit_status, publish_research, publish_competition, publish_personal, time_match_overview
from .attachment import upload_attachment, download_attachment

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
    'auto_reply_settings',
    'tags',
    'list_projects',
    'get_project_detail',
    'update_recruit_status',
    'publish_research',
    'publish_competition',
    'publish_personal',
    'upload_attachment',
    'download_attachment',
    'time_match_overview',
    'user_profile',
]
