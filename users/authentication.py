#SessionAuthentication в DRF принудительно проверяет CSRF.
#класс аутентификации который пропускает CSRF проверку

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  #пропускаем проверку CSRF
