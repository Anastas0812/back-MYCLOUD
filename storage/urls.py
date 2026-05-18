from django.urls import path
from . import views


urlpatterns = [
    path('upload/', views.upload_file_view),
    path('', views.get_files_view),  #для юзера
    path('user/<int:user_id>/', views.get_files_view),  #для админа
    path('<int:file_id>/delete/', views.delete_file_view),
    path('<int:file_id>/rename/', views.rename_file_view),
    path('<int:file_id>/download/', views.download_file_view),
    path('<int:file_id>/link/', views.get_special_link_view),
    path('download-by-link/<str:special_link>/', views.download_by_sp_link_view)
]
