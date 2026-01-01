"""
附件相关视图
包括：文件上传
"""
import os
import uuid
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from ..models import PostAttachment, PostEntity
from ..utils.auth import login_required, get_user_from_token


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f}GB"


def get_file_type_from_post_type(post_type):
    """根据post_type获取file_type
    post_type: 1-科研项目, 2-竞赛项目, 3-个人技能
    file_type: 1-科研材料, 2-大创或竞赛, 3-个人证书简历
    """
    mapping = {
        1: 1,  # 科研项目 -> 科研材料
        2: 2,  # 竞赛项目 -> 大创或竞赛
        3: 3,  # 个人技能 -> 个人证书简历
    }
    return mapping.get(post_type, 4)  # 默认其他类型


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@login_required
def upload_attachment(request):
    """上传附件接口
    
    POST /attachments/upload
    请求头:
    Authorization: Bearer <token>
    Content-Type: multipart/form-data
    
    请求参数:
    - file: 文件（必填）
    - post_id: 项目ID（必填）
    
    返回:
    {
        "code": 200,
        "msg": "上传成功",
        "data": {
            "attachment_id": "uuid",
            "post_id": 1,
            "original_filename": "example.pdf",
            "file_size": 1024,
            "formatted_size": "1.00KB",
            "mime_type": "application/pdf",
            "file_type": 1,
            "download_url": "/api/files/{file_id}/download",
            "storage_path": "uploads/..."
        }
    }
    """
    try:
        # 获取用户
        user = request.user
        
        # 获取上传的文件
        if 'file' not in request.FILES:
            return Response(
                {'code': 400, 'msg': '未提供文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # 获取post_id
        post_id = request.data.get('post_id')
        if not post_id:
            return Response(
                {'code': 400, 'msg': '未提供post_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return Response(
                {'code': 400, 'msg': 'post_id格式错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证post是否存在
        try:
            post = PostEntity.objects.get(post_id=post_id)
        except PostEntity.DoesNotExist:
            return Response(
                {'code': 404, 'msg': '项目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 验证权限：用户必须是项目的创建者
        # 对于科研项目和竞赛项目，检查是否为教师且为该项目的教师
        # 对于个人技能，检查是否为学生且为该项目的学生
        if post.post_type == 1:  # 科研项目
            from ..models import ResearchProject
            try:
                research = ResearchProject.objects.get(post=post)
                if user.identity != 1 or research.teacher.user != user:
                    return Response(
                        {'code': 403, 'msg': '无权上传该项目的附件'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ResearchProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '科研项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif post.post_type == 2:  # 竞赛项目
            from ..models import CompetitionProject
            try:
                competition = CompetitionProject.objects.get(post=post)
                if user.identity != 1 or competition.teacher.user != user:
                    return Response(
                        {'code': 403, 'msg': '无权上传该项目的附件'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except CompetitionProject.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '竞赛项目信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif post.post_type == 3:  # 个人技能
            from ..models import SkillInformation
            try:
                skill = SkillInformation.objects.get(post=post)
                if user.identity != 0 or skill.student.user != user:
                    return Response(
                        {'code': 403, 'msg': '无权上传该项目的附件'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except SkillInformation.DoesNotExist:
                return Response(
                    {'code': 404, 'msg': '个人技能信息不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'code': 400, 'msg': '不支持的项目类型'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取文件信息
        original_filename = uploaded_file.name
        file_size = uploaded_file.size
        mime_type = uploaded_file.content_type or 'application/octet-stream'
        
        # 验证文件大小（限制为50MB）
        max_file_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_file_size:
            return Response(
                {'code': 400, 'msg': f'文件大小超过限制（最大{max_file_size / (1024 * 1024)}MB）'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 生成存储路径
        # 格式：uploads/{post_type}/{post_id}/{uuid}.{ext}
        file_ext = Path(original_filename).suffix
        file_uuid = str(uuid.uuid4())
        storage_dir = f"uploads/{post.post_type}/{post_id}"
        storage_filename = f"{file_uuid}{file_ext}"
        storage_path = os.path.join(storage_dir, storage_filename)
        
        # 确保目录存在
        full_path = default_storage.path(storage_path) if hasattr(default_storage, 'path') else None
        if full_path:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # 保存文件
        saved_path = default_storage.save(storage_path, ContentFile(uploaded_file.read()))
        
        # 根据post_type确定file_type
        file_type = get_file_type_from_post_type(post.post_type)
        
        # 创建PostAttachment记录
        attachment = PostAttachment.objects.create(
            post=post,
            original_filename=original_filename,
            storage_path=saved_path,
            file_size=file_size,
            mime_type=mime_type,
            file_type=file_type,
            formatted_size=format_file_size(file_size)
        )
        
        # 生成下载URL（使用attachment的ID）
        download_url = f"/api/files/{attachment.id}/download"
        
        # 更新download_url
        attachment.download_url = download_url
        attachment.save(update_fields=['download_url'])
        
        return Response(
            {
                'code': 200,
                'msg': '上传成功',
                'data': {
                    'attachment_id': str(attachment.id),
                    'post_id': post.post_id,
                    'original_filename': attachment.original_filename,
                    'file_size': attachment.file_size,
                    'formatted_size': attachment.formatted_size,
                    'mime_type': attachment.mime_type,
                    'file_type': attachment.file_type,
                    'download_url': attachment.download_url,
                    'storage_path': attachment.storage_path
                }
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'上传失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def download_attachment(request, file_id):
    """下载附件接口
    
    GET /files/<file_id>/download
    
    返回: 文件流
    """
    try:
        # 根据UUID查找附件
        try:
            attachment = PostAttachment.objects.get(id=file_id, is_active=True)
        except PostAttachment.DoesNotExist:
            return Response(
                {'code': 404, 'msg': '附件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查文件是否存在
        if not default_storage.exists(attachment.storage_path):
            return Response(
                {'code': 404, 'msg': '文件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 读取文件
        file = default_storage.open(attachment.storage_path, 'rb')
        file_content = file.read()
        file.close()
        
        # 构建响应
        from django.http import HttpResponse
        response = HttpResponse(file_content, content_type=attachment.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
        response['Content-Length'] = attachment.file_size
        
        return response
    
    except Exception as e:
        return Response(
            {'code': 500, 'msg': f'下载失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

