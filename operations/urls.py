from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    # Area-1 URLs
    path('area1/', views.area1_list, name='area1_list'),
    path('area1/create/', views.area1_create, name='area1_create'),
    path('area1/<int:pk>/', views.area1_detail, name='area1_detail'),
    path('area1/<int:pk>/update/', views.area1_update, name='area1_update'),
    path('area1/<int:pk>/delete/', views.area1_delete, name='area1_delete'),
    path('area1/summary/', views.area1_summary, name='area1_summary'),
    path('area1/export/', views.area1_export, name='area1_export'),
    
    # Area-1 Landing and Separate Operation Forms
    path('area1/landing/', views.area1_landing, name='area1_landing'),
    path('area1/reclaiming/', views.area1_reclaiming, name='area1_reclaiming'),
    path('area1/feeding/', views.area1_feeding, name='area1_feeding'),
    path('area1/receiving/', views.area1_receiving, name='area1_receiving'),
    
    # Area-2&3 URLs
    path('area23/', views.area23_list, name='area23_list'),
    path('area23/create/', views.area23_create, name='area23_create'),
    path('area23/<int:pk>/', views.area23_detail, name='area23_detail'),
    path('area23/<int:pk>/update/', views.area23_update, name='area23_update'),
    path('area23/<int:pk>/delete/', views.area23_delete, name='area23_delete'),
    path('area23/summary/', views.area23_summary, name='area23_summary'),
    path('area23/export/', views.area23_export, name='area23_export'),
    
    # Area-2&3 Landing and Separate Operation Forms
    path('area23/landing/', views.area23_landing, name='area23_landing'),
    path('area23/feeding/', views.area23_feeding, name='area23_feeding'),
    path('area23/receiving/', views.area23_receiving, name='area23_receiving'),
    path('area23/crushing/', views.area23_crushing, name='area23_crushing'),
    path('area23/base-mix/', views.area23_base_mix, name='area23_base_mix'),
    
    # API endpoints
    path('api/area1/chart-data/', views.area1_chart_data, name='area1_chart_data'),
    path('api/area23/chart-data/', views.area23_chart_data, name='area23_chart_data'),
    path('api/equipment-presets/', views.equipment_presets, name='equipment_presets'),
] 