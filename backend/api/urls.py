from django.urls import path
from .views import (
    health_check, register, login, like, unlike, favorite, unfavorite, comment, list_comments,
    create_conversation, list_conversations, close_conversation,
    send_message, list_messages, auto_reply_settings,
    tags,
    list_projects, get_project_detail,
    publish_research, publish_competition, publish_personal,
    upload_attachment, download_attachment
)
from .views.cooperation import (
    apply_cooperation, approve_application, reject_application,reject_invitation,
    cancel_apply, invite_student, cancel_invite, agree_invite,
    check_unfinished
)

urlpatterns = [
    # 注册登录
    path('health', health_check, name='health_check'),
    path('auth/register', register, name='register'),
    path('auth/login', login, name='login'),
    path('post/like', like, name='post_like'),
    path('post/unlike', unlike, name='post_unlike'),
    path('post/favorite', favorite, name='post_favorite'),
    path('post/unfavorite', unfavorite, name='post_unfavorite'),
    path('post/comment', comment, name='post_comment'),
    path('post/comment/<int:post_id>', list_comments, name='list_comments'),

    # 附件上传与下载（新的下载路径并保留旧路径兼容）
    path('attachments/upload', upload_attachment, name='upload_attachment'),
    path('attachments/<uuid:file_id>/download', download_attachment, name='download_attachment'),
    
    # 合作流程
    path('cooperation/apply', apply_cooperation, name='apply_cooperation'),
    path('cooperation/approve', approve_application, name='approve_application'),
    path('cooperation/apply/reject', reject_application, name='reject_application'),
    path('cooperation/invite/reject', reject_invitation, name='reject_invitation'),
    path('cooperation/apply/cancel', cancel_apply, name='cancel_apply'),
    path('cooperation/invite', invite_student, name='invite_student'),
    path('cooperation/invite/cancel', cancel_invite, name='cancel_invite'),
    path('cooperation/agree', agree_invite, name='agree_invite'),
    path('cooperation/check-unfinished', check_unfinished, name='check_unfinished'),
    
    # 站内私信
    path('conversations/post', create_conversation, name='create_conversation'),
    path('conversations/lists', list_conversations, name='list_conversations'),
    path('conversations/<int:conversation_id>/close', close_conversation, name='close_conversation'),
    path('conversations/<int:conversation_id>/messages', send_message, name='send_message'),
    path('conversations/<int:conversation_id>/messages/lists', list_messages, name='list_messages'),
    path('conversations/auto_reply/settings', auto_reply_settings, name='auto_reply_settings'),
    
    # 标签
    path('tags/', tags, name='tags'),
    
    # 项目
    path('project/list', list_projects, name='list_projects'),  # 项目列表
    path('project/detail/<int:post_id>', get_project_detail, name='get_project_detail'),    # 项目详情
    
    # 项目发布接口
    path('publish/research', publish_research, name='publish_research'),   # 科研项目发布
    path('publish/competition', publish_competition, name='publish_competition'),   # 竞赛项目发布
    path('publish/personal', publish_personal, name='publish_personal'),   # 个人技能发布
    
    # 附件接口
    path('attachments/upload', upload_attachment, name='upload_attachment'),   # 上传附件
    path('attachments/<uuid:file_id>/download', download_attachment, name='download_attachment'),   # 下载附件
]

