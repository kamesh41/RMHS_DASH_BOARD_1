from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Delay, DELAY_TYPE_CHOICES, EQUIPMENT_CHOICES, AREA_CHOICES

class DelayReportForm(forms.ModelForm):
    """Form for reporting delays"""
    
    # Add date picker widget for date field
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    
    # Time pickers for start and end times
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=True
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=True
    )
    
    # Custom fields
    duration_hours = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=False,
        help_text="Duration in hours (calculated automatically)"
    )
    
    class Meta:
        model = Delay
        fields = [
            'date', 'shift', 'delay_type', 'area', 'equipment', 'equipment_id',
            'start_time', 'end_time', 'duration_hours',
            'delay_reason', 'action_taken', 'is_resolved', 'remarks'
        ]
        widgets = {
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'delay_type': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'equipment_id': forms.TextInput(attrs={'class': 'form-control'}),
            'delay_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set current date as default
        self.fields['date'].initial = timezone.now().date()
        
        # Set descriptions
        self.fields['equipment_id'].help_text = "Enter the equipment ID or tag number"
        self.fields['delay_reason'].help_text = "Describe the reason for the delay"
        self.fields['action_taken'].help_text = "Describe the action taken to resolve the delay"
        self.fields['is_resolved'].help_text = "Check if the delay has been resolved"
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Calculate duration in hours
        if start_time and end_time:
            start_datetime = timezone.datetime.combine(timezone.now().date(), start_time)
            end_datetime = timezone.datetime.combine(timezone.now().date(), end_time)
            
            # Handle overnight delays
            if end_datetime < start_datetime:
                end_datetime = end_datetime + timezone.timedelta(days=1)
            
            duration = end_datetime - start_datetime
            cleaned_data['duration_hours'] = round(duration.total_seconds() / 3600, 2)  # Convert to hours (2 decimal places)
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the created_by field to the current user
        if self.user and not instance.pk:
            instance.created_by = self.user
        
        # Set resolution time if resolved
        if instance.is_resolved and not instance.resolution_time:
            instance.resolution_time = timezone.now()
        
        if commit:
            instance.save()
        
        return instance 