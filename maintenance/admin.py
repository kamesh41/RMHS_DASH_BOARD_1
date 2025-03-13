from django.contrib import admin
from .models import MaintenanceActivity, Spare

@admin.register(MaintenanceActivity)
class MaintenanceActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'activity_type', 'maintenance_type', 'maintenance_category', 
                    'area', 'equipment', 'duration_hours', 'is_completed')
    list_filter = ('date', 'shift', 'activity_type', 'maintenance_type', 'maintenance_category', 
                   'area', 'equipment', 'is_completed', 'priority')
    search_fields = ('activity_description', 'execution_description', 'spares_required', 
                    'spares_used', 'pending_work', 'remarks', 'equipment_id')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'shift', 'activity_type', 'maintenance_type', 'maintenance_category', 'area', 'equipment', 'equipment_id')
        }),
        ('Planning Details', {
            'fields': ('activity_description', 'spares_required'),
            'classes': ('collapse',),
            'description': 'Information entered during planning phase (morning entry)'
        }),
        ('Execution Details', {
            'fields': ('execution_description', 'spares_used', 'pending_work'),
            'classes': ('collapse',),
            'description': 'Information entered during execution phase (evening entry)'
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'duration_hours')
        }),
        ('Status and Priority', {
            'fields': ('priority', 'is_completed', 'completion_time')
        }),
        ('Relationship', {
            'fields': ('related_activity',),
            'classes': ('collapse',),
            'description': 'Link between planning and execution activities'
        }),
        ('Additional Information', {
            'fields': ('remarks', 'created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(Spare)
class SpareAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_number', 'equipment_type', 'maintenance_type',
                   'quantity_available', 'minimum_stock_level', 'is_low_stock')
    list_filter = ('equipment_type', 'maintenance_type', 'last_restocked_date')
    search_fields = ('name', 'part_number', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'part_number', 'description')
        }),
        ('Inventory Details', {
            'fields': ('quantity_available', 'minimum_stock_level', 'unit_price', 'last_restocked_date')
        }),
        ('Categorization', {
            'fields': ('equipment_type', 'maintenance_type')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 