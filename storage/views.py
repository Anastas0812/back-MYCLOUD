import uuid
import os
import logging
from django.conf import settings
from django.utils import timezone
from django.http import FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import User
from .models import File
from .serializers import FileSerializer


logger = logging.getLogger(__name__)

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============


def get_file_or_404(file_id):
    #Ищет файл по id. Возвращает (file, None) или (None, Response с ошибкой)
    try:
        file = File.objects.get(id=file_id)
        return file, None
    except File.DoesNotExist:
        return None, Response(
            {'error': 'Файл не найден'},
            status=status.HTTP_404_NOT_FOUND
        )


def check_file_access(request, file):
    #Проверяет что файл принадлежит юзеру или юзер админ.
    #Возвращает Response с ошибкой или None если всё ок
    if file.owner != request.user and \
       not request.user.is_admin and \
       not request.user.is_superuser:
        return Response(
            {'error': 'У вас нет доступа к этому файлу'},
            status=status.HTTP_403_FORBIDDEN
        )
    return None


# ============ ОБРАБОТЧИКИ ============
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file_view(request):
    logger.info(f'Юзер {request.user.username} загружает файл')
    file = request.FILES.get('file')
    comment = request.data.get('comment', '')  #чтоб не упало все, если коммент не прописали

    #через админ зону переход на юзера, загрузка файла в чужое хранилище
    target_user_id = request.data.get('user_id')
    if target_user_id and request.user.is_admin:
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        target_user = request.user

    if not file:
        logger.warning(f'Юзер {request.user.username} не передал файл')
        return Response(
            {'error': 'Файл не получен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    extension = os.path.splitext(file.name)[1]  #достаем расширение файла
    unique_name = f'{uuid.uuid4().hex}{extension}'  #склеиваем уникальное имя и расширение

    user_folder = f'user_{target_user.id}'
    save_dir = os.path.join(settings.MEDIA_ROOT, user_folder)  #склейка путей безопасно для ОС
    os.makedirs(save_dir, exist_ok=True)  #создание полного пути, не упасть если папка уже создана

    file_path = os.path.join(save_dir, unique_name)
    with open(file_path, 'wb+') as dest:
        #file.chunks() встроенный метод Django, читает кусками по 64КБ
        for chunk in file.chunks():
            dest.write(chunk)

    #сохраним в БД
    db_file = File.objects.create(
        owner=target_user,
        original_name=file.name,
        size=file.size,
        comment=comment,
        file_path=f'{user_folder}/{unique_name}',
        special_link=uuid.uuid4().hex
    )

    serializer = FileSerializer(db_file)
    logger.info(f'Файл {file.name} загружен юзером {request.user.username}')
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_files_view(request, user_id=None):  #даем админу доступ к файлам юзеров
    if user_id and request.user.is_admin:
        files = File.objects.filter(owner_id=user_id)
    else:
        files = File.objects.filter(owner=request.user)

    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_file_view(request, file_id):
    logger.info(f'Юзер {request.user.username} удаляет файл id={file_id}')
    file, error = get_file_or_404(file_id)
    if error:
        logger.warning(f'Файл id={file_id} не найден')
        return error

    error = check_file_access(request, file)
    if error:
        logger.warning(f'Юзер {request.user.username} пытается удалить чужой файл')
        return error

    #удаление с диска
    full_path = os.path.join(settings.MEDIA_ROOT, file.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    #удаление из БД
    file.delete()
    logger.info(f'Файл id={file_id} удалён')
    return Response(
        {'message': 'Файл успешно удален'},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def rename_file_view(request, file_id):
    file, error = get_file_or_404(file_id)
    if error:
        return error

    error = check_file_access(request, file)
    if error:
        return error

    new_name = request.data.get('new_name')
    new_comment = request.data.get('comment')

    if new_name:
        file.original_name = new_name
    if new_comment is not None:
        file.comment = new_comment

    file.save()
    serializer = FileSerializer(file)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file_view(request, file_id):
    file, error = get_file_or_404(file_id)
    if error:
        return error

    error = check_file_access(request, file)
    if error:
        return error

    #апдейт даты скачивания
    file.last_download = timezone.now()
    file.save()

    #отдаем файл с оригинальным именем
    full_path = os.path.join(settings.MEDIA_ROOT, file.file_path)  #сборка полного пути
    response = FileResponse(
        open(full_path, 'rb'),
        as_attachment=True,  #скачать файл, а не открывать в браузере
        filename=file.original_name  #не уникальное а ОРИГИНАЛЬНОЕ имя!
    )
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_special_link_view(request, file_id):
    file, error = get_file_or_404(file_id)
    if error:
        return error

    error = check_file_access(request, file)
    if error:
        return error

    #отдаем полную ссылку
    link = request.build_absolute_uri(
        f'/api/storage/download-by-link/{file.special_link}/'
    )
    return Response({'special_link': link})


#скачивание файла через спец. ссылку, используемую внешними пользователями (без авторизации)
@api_view(['GET'])
def download_by_sp_link_view(_, special_link):
    try:
        file = File.objects.get(special_link=special_link)
    except File.DoesNotExist:
        return Response(
            {'error': 'Файл не найден'},
            status=status.HTTP_404_NOT_FOUND
        )

    file.last_download = timezone.now()
    file.save()

    full_path = os.path.join(settings.MEDIA_ROOT, file.file_path)
    response = FileResponse(
        open(full_path, 'rb'),
        as_attachment=True,
        filename=file.original_name
    )
    return response
