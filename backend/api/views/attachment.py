import os
import mimetypes
from uuid import UUID, uuid4
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.urls import reverse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models.attachment import PostAttachment
from ..models.post import PostEntity


UPLOAD_ROOT = os.path.join(getattr(settings, 'BASE_DIR', ''), 'uploads')


def _type_folder(file_type: int) -> str:
    mapping = {
        1: 'research',   # 科研材料
        2: 'competition',  # 大创或竞赛
        3: 'resume',     # 个人证书简历
        4: '其他',    # 其他
    }
    return mapping.get(int(file_type), 'others')


def _format_size(num: int) -> str:
    units = ['B', 'KB', 'MB', 'GB']
    size = float(num)
    for unit in units:
        if size < 1024 or unit == 'GB':
            return f"{size:.2f}{unit}"
        size /= 1024
    return f"{num}B"


def _storage() -> FileSystemStorage:
    os.makedirs(UPLOAD_ROOT, exist_ok=True)
    return FileSystemStorage(location=UPLOAD_ROOT)


def _serialize_attachment(att: PostAttachment):
    return {
        'id': str(att.id),
        'post_id': att.post_id if att.post_id else None,
        'original_filename': att.original_filename,
        'storage_path': att.storage_path,
        'file_size': att.file_size,
        'mime_type': att.mime_type,
        'file_type': att.file_type,
        'created_at': att.created_at.isoformat() if att.created_at else None,
        'updated_at': att.updated_at.isoformat() if att.updated_at else None,
        'is_active': att.is_active,
        'download_url': att.download_url,
        'formatted_size': att.formatted_size,
    }


@api_view(['POST'])
def upload_attachment(request):
    """上传附件按类型/年月落盘，仅返回元数据，不落库"""
    uploaded_file = request.FILES.get('file')
    file_type = request.data.get('type')
    post_id = request.data.get('post_id')

    if not uploaded_file:
        return Response({'code': 400, 'msg': '缺少文件'}, status=status.HTTP_400_BAD_REQUEST)
    if not file_type:
        return Response({'code': 400, 'msg': '缺少文件类型type'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        file_type_int = int(file_type)
    except ValueError:
        return Response({'code': 400, 'msg': 'type 必须是 1/2/3/4'}, status=status.HTTP_400_BAD_REQUEST)

    if file_type_int not in [1, 2, 3, 4]:
        return Response({'code': 400, 'msg': 'type 必须是 1/2/3/4'}, status=status.HTTP_400_BAD_REQUEST)

    post_obj = None
    if post_id is not None:
        try:
            post_obj = PostEntity.objects.get(post_id=post_id)
        except PostEntity.DoesNotExist:
            return Response({'code': 404, 'msg': 'post 不存在'}, status=status.HTTP_404_NOT_FOUND)

    folder = _type_folder(file_type_int)
    now = timezone.now()
    dated_folder = os.path.join(folder, str(now.year), f"{now.month:02d}")
    storage = _storage()
    filename = f"{uuid4()}_{uploaded_file.name}"
    saved_path = storage.save(os.path.join(dated_folder, filename), uploaded_file)

    mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    file_size = uploaded_file.size

    file_id = uuid4()
    download_url = request.build_absolute_uri(
        reverse('download_attachment', kwargs={'file_id': file_id})
    )

    now_iso = now.isoformat()
    data = {
        'id': str(file_id),
        'post_id': post_id if post_id else None,
        'original_filename': filename,
        'storage_path': saved_path,
        'file_size': file_size,
        'mime_type': mime_type,
        'file_type': file_type_int,
        'formatted_size': _format_size(file_size),
        'download_url': download_url,
        'created_at': now_iso,
        'updated_at': now_iso,
        'is_active': True,
    }
    return Response({'code': 200, 'data': data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def download_attachment(request, file_id):
    """推荐的新下载路径 /attachments/{file_id}/download"""
    return _download_core(file_id)


def _download_core(file_id):
    try:
        UUID(str(file_id))
        attachment = PostAttachment.objects.get(id=file_id, is_active=True)
    except (ValueError, PostAttachment.DoesNotExist):
        raise Http404('文件不存在')

    storage = _storage()
    if not storage.exists(attachment.storage_path):
        raise Http404('文件不存在')

    file_handle = storage.open(attachment.storage_path, 'rb')
    mime_type = attachment.mime_type or 'application/octet-stream'
    response = FileResponse(file_handle, content_type=mime_type)
    response['Content-Length'] = attachment.file_size
    response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
    return response
