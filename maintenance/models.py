from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Choices for shift
SHIFT_CHOICES = [
    ('A', 'Shift A (6:00 AM - 2:00 PM)'),
    ('B', 'Shift B (2:00 PM - 10:00 PM)'),
    ('C', 'Shift C (10:00 PM - 6:00 AM)'),
    ('G', 'General Shift (9:00 AM - 6:30 PM)'),
]

# Choices for maintenance type
MAINTENANCE_TYPE_CHOICES = [
    ('MECHANICAL', 'Mechanical'),
    ('ELECTRICAL', 'Electrical'),
    ('OPERATION', 'Operation'),
    ('CIVIL', 'Civil'),
    ('OTHER', 'Other'),
]

# Choices for maintenance category
MAINTENANCE_CATEGORY_CHOICES = [
    ('PREVENTIVE', 'Preventive Maintenance'),
    ('BREAKDOWN', 'Breakdown Maintenance'),
    ('CORRECTIVE', 'Corrective Maintenance'),
    ('PREDICTIVE', 'Predictive Maintenance'),
    ('ROUTINE', 'Routine Maintenance'),
]

# Choices for equipment
EQUIPMENT_CHOICES = [
    ('CONVEYOR', 'Conveyor'),
    ('STACKER', 'Stacker'),
    ('RECLAIMER', 'Reclaimer'),
    ('CRUSHER', 'Crusher'),
    ('SCREEN', 'Screen'),
    ('WAGON_TIPPLER', 'Wagon Tippler'),
    ('SIDE_ARM_CHARGER', 'Side Arm Charger'),
    ('OTHER', 'Other'),
]

# Choices for area
AREA_CHOICES = [
    ('AREA_1', 'Area-1'),
    ('AREA_2', 'Area-2'),
    ('AREA_3', 'Area-3'),
]

# Choices for priority
PRIORITY_CHOICES = [
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
]

# Choices for activity type
ACTIVITY_TYPE_CHOICES = [
    ('PLANNED', 'Planned Activity'),
    ('EXECUTION', 'Execution Report'),
]

class MaintenanceActivity(models.Model):
    """Model for maintenance activities"""
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    
    # Activity type (new field)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE_CHOICES, default='PLANNED')
    
    # Maintenance details
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    maintenance_category = models.CharField(max_length=20, choices=MAINTENANCE_CATEGORY_CHOICES)
    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    equipment = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES)
    equipment_id = models.CharField(max_length=50, help_text="Equipment ID or Tag Number")
    
    # Planning details (morning entry)
    activity_description = models.TextField(help_text="Description of maintenance activity")
    spares_required = models.TextField(blank=True, null=True, help_text="Spares required for planned maintenance")
    
    # Execution details (evening entry)
    execution_description = models.TextField(blank=True, null=True, help_text="Description of actual work executed")
    spares_used = models.TextField(blank=True, null=True, help_text="Spares actually used in maintenance")
    pending_work = models.TextField(blank=True, null=True, help_text="Description of pending work or jobs")
    
    # Time details
    start_time = models.TimeField(help_text="Activity start time")
    end_time = models.TimeField(help_text="Activity end time")
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    
    # Status and priority
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_completed = models.BooleanField(default=False)
    completion_time = models.DateTimeField(null=True, blank=True)
    
    # Related activity (for connecting plan with execution)
    related_activity = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, 
                                         related_name='execution_reports', 
                                         help_text="Link to the related planning/execution activity")
    
    # Common fields
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Maintenance Activity"
        verbose_name_plural = "Maintenance Activities"
    
    def __str__(self):
        activity_prefix = "Plan" if self.activity_type == "PLANNED" else "Execution"
        return f"{activity_prefix}: {self.maintenance_type} - {self.date} - {self.equipment}"
    
    def save(self, *args, **kwargs):
        # Calculate duration in hours if not provided
        if not self.duration_hours and self.start_time and self.end_time:
            start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
            end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
            
            # Handle overnight maintenance
            if end_datetime < start_datetime:
                end_datetime = end_datetime + timezone.timedelta(days=1)
            
            duration = end_datetime - start_datetime
            self.duration_hours = duration.total_seconds() / 3600  # Convert to hours
        
        # Set completion time if completed
        if self.is_completed and not self.completion_time:
            self.completion_time = timezone.now()
        
        super().save(*args, **kwargs)


class Spare(models.Model):
    """Model for spare parts inventory"""
    name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50)
    description = models.TextField()
    
    # Inventory details
    quantity_available = models.PositiveIntegerField(default=0)
    minimum_stock_level = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Categorization
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    
    # Common fields
    last_restocked_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Spare Part"
        verbose_name_plural = "Spare Parts"
    
    def __str__(self):
        return f"{self.name} - {self.part_number}"
    
    @property
    def is_low_stock(self):
        """Check if the spare part is low in stock"""
        return self.quantity_available <= self.minimum_stock_level 