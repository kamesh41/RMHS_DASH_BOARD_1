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
    ('IRON_ORE_FINES', 'Iron Ore Fines'),
    ('LIMESTONE', 'Limestone'),
    ('DOLOMITE', 'Dolomite'),
    ('COAL', 'Coal'),
    ('COKE', 'Coke'),
    ('COKE_FINES', 'Coke Fines'),
    ('SINTER', 'Sinter'),
    ('SINTER_FINES', 'Sinter Fines'),
    ('PELLET', 'Pellet'),
    ('LUMP_ORE', 'Lump Ore'),
    ('QUARTZITE', 'Quartzite'),
    ('SLAG', 'Slag'),
    ('BASE_MIX', 'Base Mix'),
    ('OTHER', 'Other'),
]

class Area1Operation(models.Model):
    """Model for Area-1 operations (Reclaiming, Feeding to BF/SMS, Receiving from BF)"""
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    
    # Reclaiming
    reclaiming_material = models.CharField(max_length=100, blank=True)
    reclaiming_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reclaiming_equipment = models.CharField(max_length=100, blank=True)
    reclaiming_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    reclaiming_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Feeding
    feeding_destination = models.CharField(max_length=50, help_text="Destination (BF/SMS)")
    feeding_material = models.CharField(max_length=100, blank=True)
    feeding_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    feeding_equipment = models.CharField(max_length=100, blank=True)
    feeding_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    feeding_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Receiving
    receiving_source = models.CharField(max_length=50, help_text="Source (BF)")
    receiving_material = models.CharField(max_length=100, blank=True)
    receiving_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receiving_equipment = models.CharField(max_length=100, blank=True)
    receiving_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    receiving_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Common fields
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # This method will return the appropriate material name, including custom ones
    def get_reclaiming_material_name(self):
        if self.reclaiming_material == 'OTHER' and self.reclaiming_other_material:
            return self.reclaiming_other_material
        return dict(MATERIAL_CHOICES).get(self.reclaiming_material, '')
    
    def get_feeding_material_name(self):
        if self.feeding_material == 'OTHER' and self.feeding_other_material:
            return self.feeding_other_material
        return dict(MATERIAL_CHOICES).get(self.feeding_material, '')
    
    def get_receiving_material_name(self):
        if self.receiving_material == 'OTHER' and self.receiving_other_material:
            return self.receiving_other_material
        return dict(MATERIAL_CHOICES).get(self.receiving_material, '')
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Area-1 Operation"
        verbose_name_plural = "Area-1 Operations"
    
    def __str__(self):
        return f"Area-1 Operation - {self.date} - Shift {self.shift}"


class Area23Operation(models.Model):
    """Model for Area-2 & Area-3 operations (Feeding, Receiving, Crushing, Base Mix Handling)"""
    date = models.DateField(default=timezone.now)
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    
    # Feeding
    feeding_material = models.CharField(max_length=100, blank=True)
    feeding_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    feeding_equipment = models.CharField(max_length=100, blank=True)
    feeding_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    feeding_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Receiving
    receiving_material = models.CharField(max_length=100, blank=True)
    receiving_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receiving_equipment = models.CharField(max_length=100, blank=True)
    receiving_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    receiving_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Crushing
    crushing_material = models.CharField(max_length=100, blank=True)
    crushing_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    crushing_equipment = models.CharField(max_length=100, blank=True)
    crushing_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    crushing_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Base Mix Handling
    base_mix_material = models.CharField(max_length=100, blank=True)
    base_mix_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    base_mix_equipment = models.CharField(max_length=100, blank=True)
    base_mix_other_material = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if 'Other' material is selected")
    base_mix_other_equipment = models.CharField(max_length=50, blank=True, null=True, help_text="Specify if equipment is not standard")
    
    # Common fields
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # This method will return the appropriate material name, including custom ones
    def get_feeding_material_name(self):
        if self.feeding_material == 'OTHER' and self.feeding_other_material:
            return self.feeding_other_material
        return dict(MATERIAL_CHOICES).get(self.feeding_material, '')
    
    def get_receiving_material_name(self):
        if self.receiving_material == 'OTHER' and self.receiving_other_material:
            return self.receiving_other_material
        return dict(MATERIAL_CHOICES).get(self.receiving_material, '')
    
    def get_crushing_material_name(self):
        if self.crushing_material == 'OTHER' and self.crushing_other_material:
            return self.crushing_other_material
        return dict(MATERIAL_CHOICES).get(self.crushing_material, '')
    
    def get_base_mix_material_name(self):
        if self.base_mix_material == 'OTHER' and self.base_mix_other_material:
            return self.base_mix_other_material
        return dict(MATERIAL_CHOICES).get(self.base_mix_material, '')
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Area-2 & 3 Operation"
        verbose_name_plural = "Area-2 & 3 Operations"
    
    def __str__(self):
        return f"Area-2 & 3 Operation - {self.date} - Shift {self.shift}" 