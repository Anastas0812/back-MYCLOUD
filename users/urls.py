from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('', views.get_users_view),
    path('<int:user_id>/', views.delete_user_view),
    path('<int:user_id>/toggle-admin/', views.toggle_admin_view),
]
