from django.contrib import admin
from .models import Rake

@admin.register(Rake)
class RakeAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'rake_id', 'material_type', 'total_wagons', 
                    'total_quantity', 'status', 'demurrage_hours')
    list_filter = ('date', 'shift', 'material_type', 'status', 'supplier')
    search_fields = ('rake_id', 'supplier', 'remarks', 'unloading_equipment')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'shift', 'rake_id', 'material_type', 'supplier')
        }),
        ('Quantity Details', {
            'fields': ('total_wagons', 'wagon_capacity', 'total_quantity')
        }),
        ('Time Details', {
            'fields': ('arrival_time', 'unloading_start_time', 'unloading_end_time')
        }),
        ('Status and Unloading', {
            'fields': ('status', 'unloading_equipment', 'demurrage_hours')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'created_by', 'created_at', 'updated_at')
        }),
    ) 