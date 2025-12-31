"""
Django 模型包
使用模型包结构组织所有数据模型
"""
from .user import User, StudentEntity, TeacherEntity
from .post import PostEntity
from .tag import Tag, PostTag
from .project import ResearchProject, CompetitionProject, SkillInformation
from .interaction import Like, Favorite, Comment
from .message import Conversation, Message
from .cooperation import TeacherStudentCooperation
from .skill import Skill, StudentSkill
from .direction import TechStack, Direction, ResearchDirection, PostDirection
from .attachment import PostAttachment

__all__ = [
    'User',
    'StudentEntity',
    'TeacherEntity',
    'PostEntity',
    'Tag',
    'PostTag',
    'ResearchProject',
    'CompetitionProject',
    'SkillInformation',
    'Like',
    'Favorite',
    'Comment',
    'Conversation',
    'Message',
    'TeacherStudentCooperation',
    'Skill',
    'StudentSkill',
    'TechStack',
    'Direction',
    'ResearchDirection',
    'PostDirection',
    'PostAttachment',
]

