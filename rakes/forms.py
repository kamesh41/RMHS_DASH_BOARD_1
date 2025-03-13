from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Rake

class RakeEntryForm(forms.ModelForm):
    """Form for rake completion reports"""
    
    # Add date picker widget for date fields
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )
    
    # Add datetime picker for time fields
    arrival_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )
    
    unloading_start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True
    )
    
    unloading_end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    
    class Meta:
        model = Rake
        fields = [
            'date', 'shift', 'rake_id', 'material_type', 'supplier', 
            'total_wagons', 'wagon_capacity', 'total_quantity',
            'arrival_time', 'unloading_start_time', 'unloading_end_time',
            'status', 'unloading_equipment', 'demurrage_hours', 'remarks'
        ]
        widgets = {
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'rake_id': forms.TextInput(attrs={'class': 'form-control'}),
            'material_type': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'total_wagons': forms.NumberInput(attrs={'class': 'form-control'}),
            'wagon_capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'unloading_equipment': forms.TextInput(attrs={'class': 'form-control'}),
            'demurrage_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set current date as default
        self.fields['date'].initial = timezone.now().date()
        
        # If it's a new rake entry, calculate total quantity on input change
        if not self.instance.pk:
            self.fields['total_quantity'].widget.attrs.update({
                'readonly': 'readonly',
            })
    
    def clean(self):
        cleaned_data = super().clean()
        arrival_time = cleaned_data.get('arrival_time')
        unloading_start_time = cleaned_data.get('unloading_start_time')
        unloading_end_time = cleaned_data.get('unloading_end_time')
        
        # Validate time sequence
        if arrival_time and unloading_start_time and arrival_time > unloading_start_time:
            self.add_error('unloading_start_time', 'Unloading cannot start before rake arrival')
        
        if unloading_start_time and unloading_end_time and unloading_start_time > unloading_end_time:
            self.add_error('unloading_end_time', 'Unloading cannot end before it starts')
        
        # Calculate total quantity if not provided
        total_wagons = cleaned_data.get('total_wagons')
        wagon_capacity = cleaned_data.get('wagon_capacity')
        if total_wagons and wagon_capacity:
            cleaned_data['total_quantity'] = total_wagons * wagon_capacity
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the created_by field to the current user
        if self.user and not instance.pk:
            instance.created_by = self.user
        
        if commit:
            instance.save()
        
        return instance 