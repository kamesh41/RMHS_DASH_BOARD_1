from django.contrib import admin
from .models import Delay

@admin.register(Delay)
class DelayAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift', 'delay_type', 'area', 'equipment', 'duration_hours', 'is_resolved')
    list_filter = ('date', 'shift', 'delay_type', 'area', 'equipment', 'is_resolved')
    search_fields = ('delay_reason', 'action_taken', 'remarks', 'equipment_id')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'shift', 'delay_type', 'area', 'equipment', 'equipment_id')
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'duration_hours')
        }),
        ('Description and Resolution', {
            'fields': ('delay_reason', 'action_taken', 'is_resolved', 'resolution_time')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'created_by', 'created_at', 'updated_at')
        }),
    ) 