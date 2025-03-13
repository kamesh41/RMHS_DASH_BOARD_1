from django.urls import path
from . import views

app_name = 'delays'

urlpatterns = [
    path('', views.delay_list, name='list'),
    path('create/', views.delay_create, name='create'),
    path('<int:pk>/', views.delay_detail, name='detail'),
    path('<int:pk>/update/', views.delay_update, name='update'),
    path('<int:pk>/delete/', views.delay_delete, name='delete'),
    path('<int:pk>/resolve/', views.delay_resolve, name='resolve'),
] 