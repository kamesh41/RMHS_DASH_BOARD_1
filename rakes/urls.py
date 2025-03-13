from django.urls import path
from . import views

app_name = 'rakes'

urlpatterns = [
    path('', views.rake_list, name='list'),
    path('create/', views.rake_create, name='create'),
    path('<int:pk>/', views.rake_detail, name='detail'),
    path('<int:pk>/update/', views.rake_update, name='update'),
    path('<int:pk>/delete/', views.rake_delete, name='delete'),
    path('<int:pk>/complete/', views.rake_complete, name='complete'),
] 