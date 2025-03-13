from django import forms
from .models import MaintenanceActivity, Spare

class MaintenancePlanningForm(forms.ModelForm):
    """Form for planning maintenance activities (morning entry)"""
    
    class Meta:
        model = MaintenanceActivity
        fields = [
            'date', 'shift', 'maintenance_type', 'maintenance_category', 
            'area', 'equipment', 'equipment_id', 'activity_description', 
            'spares_required', 'start_time', 'end_time', 'priority', 'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'activity_description': forms.Textarea(attrs={'rows': 4}),
            'spares_required': forms.Textarea(attrs={'rows': 4}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'shift': forms.HiddenInput(),  # Hide the shift field since it's always general
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always set activity_type to PLANNED and shift to General
        self.instance.activity_type = 'PLANNED'
        self.instance.shift = 'G'  # G is for General Shift
        # Disable the shift field in case it's shown
        if 'shift' in self.fields:
            self.fields['shift'].disabled = True
            self.fields['shift'].initial = 'G'


class MaintenanceExecutionForm(forms.ModelForm):
    """Form for execution of maintenance activities (evening entry)"""
    
    class Meta:
        model = MaintenanceActivity
        fields = [
            'date', 'shift', 'maintenance_type', 'maintenance_category', 
            'area', 'equipment', 'equipment_id', 'execution_description', 
            'spares_used', 'pending_work', 'start_time', 'end_time', 
            'is_completed', 'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'execution_description': forms.Textarea(attrs={'rows': 4}),
            'spares_used': forms.Textarea(attrs={'rows': 4}),
            'pending_work': forms.Textarea(attrs={'rows': 4}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
            'shift': forms.HiddenInput(),  # Hide the shift field since it's always general
        }
    
    def __init__(self, *args, **kwargs):
        planning_activity = kwargs.pop('planning_activity', None)
        super().__init__(*args, **kwargs)
        
        # Always set activity_type to EXECUTION and shift to General
        self.instance.activity_type = 'EXECUTION'
        self.instance.shift = 'G'  # G is for General Shift
        
        # Disable the shift field in case it's shown
        if 'shift' in self.fields:
            self.fields['shift'].disabled = True
            self.fields['shift'].initial = 'G'
        
        # If a planning activity was provided, pre-fill fields
        if planning_activity:
            self.instance.related_activity = planning_activity
            
            # Pre-fill fields from the planning activity
            self.initial.update({
                'date': planning_activity.date,
                'maintenance_type': planning_activity.maintenance_type,
                'maintenance_category': planning_activity.maintenance_category,
                'area': planning_activity.area,
                'equipment': planning_activity.equipment,
                'equipment_id': planning_activity.equipment_id,
                'start_time': planning_activity.start_time,
                'end_time': planning_activity.end_time,
            })


class SpareForm(forms.ModelForm):
    """Form for managing spare parts inventory"""
    
    class Meta:
        model = Spare
        fields = [
            'name', 'part_number', 'description', 'quantity_available',
            'minimum_stock_level', 'unit_price', 'equipment_type',
            'maintenance_type', 'last_restocked_date'
        ]
        widgets = {
            'last_restocked_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        } 