from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Maintenance Activities
    path('', views.maintenance_list, name='list'),
    
    # Planning views
    path('plan/create/', views.maintenance_create_plan, name='create_plan'),
    
    # Execution views
    path('execution/create/', views.maintenance_create_execution, name='create_execution'),
    path('execution/create/<int:plan_pk>/', views.maintenance_create_execution, name='create_execution_from_plan'),
    
    # Common views
    path('<int:pk>/', views.maintenance_detail, name='detail'),
    path('<int:pk>/update/', views.maintenance_update, name='update'),
    path('<int:pk>/delete/', views.maintenance_delete, name='delete'),
    path('<int:pk>/complete/', views.maintenance_complete, name='complete'),
    
    # Pending activities view
    path('pending/', views.pending_activities, name='pending'),
    
    # Spare Parts
    path('spares/', views.spare_list, name='spare_list'),
    path('spares/create/', views.spare_create, name='spare_create'),
    path('spares/<int:pk>/', views.spare_detail, name='spare_detail'),
    path('spares/<int:pk>/update/', views.spare_update, name='spare_update'),
    path('spares/<int:pk>/delete/', views.spare_delete, name='spare_delete'),
] 