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

# Choices for delay types
DELAY_TYPE_CHOICES = [
    ('MECHANICAL', 'Mechanical'),
    ('ELECTRICAL', 'Electrical'),
    ('OPERATIONAL', 'Operational'),
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

class Delay(models.Model):
    """Model for delay reports (Mechanical, Electrical, Operational)"""
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    
    # Delay details
    delay_type = models.CharField(max_length=20, choices=DELAY_TYPE_CHOICES)
    area = models.CharField(max_length=10, choices=AREA_CHOICES)
    equipment = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES)
    equipment_id = models.CharField(max_length=50, help_text="Equipment ID or Tag Number")
    
    # Time details
    start_time = models.TimeField(help_text="Delay start time")
    end_time = models.TimeField(help_text="Delay end time")
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    
    # Description and resolution
    delay_reason = models.TextField(help_text="Reason for the delay")
    action_taken = models.TextField(help_text="Action taken to resolve the delay")
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolution_time = models.DateTimeField(null=True, blank=True)
    
    # Common fields
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delays')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Delay Report"
        verbose_name_plural = "Delay Reports"
    
    def __str__(self):
        return f"{self.delay_type} Delay - {self.date} - {self.equipment} - {self.duration_hours} hrs"
    
    def save(self, *args, **kwargs):
        # Calculate duration in hours if not provided
        if not self.duration_hours and self.start_time and self.end_time:
            start_datetime = timezone.datetime.combine(timezone.now().date(), self.start_time)
            end_datetime = timezone.datetime.combine(timezone.now().date(), self.end_time)
            
            # Handle overnight delays
            if end_datetime < start_datetime:
                end_datetime = end_datetime + timezone.timedelta(days=1)
            
            duration = end_datetime - start_datetime
            self.duration_hours = duration.total_seconds() / 3600  # Convert to hours
        
        # Set resolution time if resolved
        if self.is_resolved and not self.resolution_time:
            self.resolution_time = timezone.now()
        
        super().save(*args, **kwargs) 