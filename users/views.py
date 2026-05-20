import logging
from storage.models import File
from .models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer


#Session Authentication как способ аутентификации юзера

logger = logging.getLogger(__name__)


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============


def get_user_or_404(user_id):
    #Ищет юзера по id.
    #Возвращает (user, None) или (None, Response с ошибкой)
    try:
        user = User.objects.get(id=user_id)
        return user, None
    except User.DoesNotExist:
        return None, Response(
            {'error': 'Пользователь не найден'},
            status=status.HTTP_404_NOT_FOUND
        )

# ============ ОБРАБОТЧИКИ ============


@api_view(['POST'])
def register_view(request):  #регистрация пользователя
    logger.info(f'Попытка регистрации: {request.data.get("username")}')
    # request.data — JSON фронта
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()  # сохраняет в БД
        logger.info(f'Успешная регистрация: {request.data.get("username")}')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    logger.warning(f'Ошибка регистрации: {serializer.errors}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):  #логин пользователя
    username = request.data.get('username')
    password = request.data.get('password')

    logger.info(f'Попытка входа: {username}')
    #authenticate идет в БД, проверяет логин и хэш пароля
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)  #старт сессии
        logger.info(f'Успешный вход: {username}')
        return Response({
            'message': 'Вход выполнен успешно',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        })

    logger.warning(f'Неудачная попытка входа: {username}')
    return Response(
        {'error': 'Неверный логин или пароль'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
def logout_view(request):  #логаут пользователя
    logout(request)  #окончание сессии, удаление из бд
    return Response({'message': 'Вы вышли из системы'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_users_view(request):  #получение списка пользователей
    logger.info(f'Запрос списка юзеров от {request.user.username}')
    users = User.objects.all()
    users_data = []
    for user in users:
        files = File.objects.filter(owner=user)
        total_size = sum(f.size for f in files)
        files_count = files.count()

        users_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'email': user.email,
            'is_admin': user.is_admin,
            #хранилище
            'storage': {
                'files_count': files_count,
                'total_size': total_size,  #байты
            }
        })
    logger.info(f'Список юзеров сформирован: {len(users_data)} записей')
    return Response(users_data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user_view(request, user_id):  #удаление юзера
    logger.info(f'Админ {request.user.username} удаляет юзера id={user_id}')
    user, error = get_user_or_404(user_id)
    if error:
        return error

    user.delete()
    logger.info(f'Юзер id={user_id} удалён')
    return Response(
        {'message': f'Пользователь {user.username} удален'},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def toggle_admin_view(request, user_id):  #изменение значения признака юзера
    user, error = get_user_or_404(user_id)
    if error:
        return error

    user.is_admin = not user.is_admin
    user.save()
    return Response({
        'message': 'Права изменены успешно',
        'is_admin': user.is_admin
    })
