from django.contrib import admin
from .models import Area1Operation, Area23Operation

@admin.register(Area1Operation)
class Area1OperationAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'reclaiming_material', 'reclaiming_quantity', 
                    'feeding_material', 'feeding_quantity', 'receiving_material', 'receiving_quantity')
    list_filter = ('date', 'shift', 'reclaiming_material', 'feeding_material', 'receiving_material')
    search_fields = ('remarks', 'reclaiming_equipment', 'feeding_equipment', 'receiving_equipment')
    date_hierarchy = 'date'

@admin.register(Area23Operation)
class Area23OperationAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'feeding_material', 'feeding_quantity', 
                    'receiving_material', 'receiving_quantity', 'crushing_material', 'crushing_quantity')
    list_filter = ('date', 'shift', 'feeding_material', 'receiving_material', 'crushing_material')
    search_fields = ('remarks', 'feeding_equipment', 'receiving_equipment', 'crushing_equipment')
    date_hierarchy = 'date' 