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

# Choices for material types
MATERIAL_CHOICES = [
    ('IRON_ORE', 'Iron Ore'),
    ('LIMESTONE', 'Limestone'),
    ('DOLOMITE', 'Dolomite'),
    ('COAL', 'Coal'),
    ('COKE', 'Coke'),
    ('OTHER', 'Other'),
]

# Choices for rake status
RAKE_STATUS_CHOICES = [
    ('RECEIVED', 'Received'),
    ('UNLOADING', 'Unloading in Progress'),
    ('COMPLETED', 'Unloading Completed'),
    ('DISPATCHED', 'Dispatched'),
]

class Rake(models.Model):
    """Model for rake completion reports"""
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    
    # Rake details
    rake_id = models.CharField(max_length=50, help_text="Rake ID or Number")
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    supplier = models.CharField(max_length=100, help_text="Material supplier")
    
    # Quantity details
    total_wagons = models.PositiveIntegerField(help_text="Total number of wagons")
    wagon_capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity per wagon in MT")
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total quantity in MT")
    
    # Time details
    arrival_time = models.DateTimeField(help_text="Rake arrival time")
    unloading_start_time = models.DateTimeField(help_text="Unloading start time")
    unloading_end_time = models.DateTimeField(null=True, blank=True, help_text="Unloading end time")
    
    # Status
    status = models.CharField(max_length=20, choices=RAKE_STATUS_CHOICES, default='RECEIVED')
    
    # Unloading details
    unloading_equipment = models.CharField(max_length=50, help_text="Equipment used for unloading")
    demurrage_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Demurrage hours if any")
    
    # Common fields
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rakes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Rake Report"
        verbose_name_plural = "Rake Reports"
    
    def __str__(self):
        return f"Rake {self.rake_id} - {self.material_type} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Calculate total quantity if not provided
        if not self.total_quantity and self.total_wagons and self.wagon_capacity:
            self.total_quantity = self.total_wagons * self.wagon_capacity
        
        # Update status based on times
        if self.unloading_end_time:
            self.status = 'COMPLETED'
        elif self.unloading_start_time:
            self.status = 'UNLOADING'
        
        super().save(*args, **kwargs)
    
    @property
    def unloading_duration_hours(self):
        """Calculate unloading duration in hours"""
        if self.unloading_start_time and self.unloading_end_time:
            duration = self.unloading_end_time - self.unloading_start_time
            return duration.total_seconds() / 3600  # Convert to hours
        return None 