import re
from rest_framework import serializers
from .models import User


#валидация email происходит в views.py при регистрации юзера (is_valid())


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  #пароль только запись

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'password', 'is_admin']

    def validate_username(self, value):
        #только латинские буквы и цифры, первый символ — буква, длина от 4 до 20 символов;
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]{3,19}$', value):
            raise serializers.ValidationError(
                "Логин: только латинские буквы и цифры, "
                "первый символ — буква, длина от 4 до 20 символов"
            )
        return value

    def validate_password(self, value):
        #не менее 6 символов: как минимум одна заглавная буква, одна цифра и один специальный символ.
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Нужна хотя бы одна заглавная латинская буква")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Нужна хотя бы одна цифра")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Нужен хотя бы один специальный символ "
                                              "(например, !, @, #, $, %, ^, &, *, (, )")
        return value


    def create(self, validated_data):
        # create_user() - хэш пароля встроенный метод джанго
        user = User.objects.create_user(**validated_data)
        return user
