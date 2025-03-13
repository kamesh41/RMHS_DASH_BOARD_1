from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet, formset_factory, BaseFormSet
from django.utils import timezone
from .models import Area1Operation, Area23Operation, SHIFT_CHOICES, MATERIAL_CHOICES
from .constants import (
    EQUIPMENT_PRESETS,
    RECLAIMING_EQUIPMENT_CHOICES,
    FEEDING_EQUIPMENT_CHOICES,
    RECEIVING_EQUIPMENT_CHOICES,
    CRUSHING_EQUIPMENT_CHOICES,
    BASE_MIX_EQUIPMENT_CHOICES,
    DESTINATION_CHOICES,
    SOURCE_CHOICES
)

# Custom Required Formset
class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


# Area 1 Forms
class Area1BatchEntryForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    shift = forms.ChoiceField(
        choices=SHIFT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the current date as default
        self.initial['date'] = timezone.now().date()


# Area 2&3 Forms
class Area23BatchEntryForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    shift = forms.ChoiceField(
        choices=SHIFT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the current date as default
        self.initial['date'] = timezone.now().date()


# Form for individual reclaiming items in batch entry
class ReclaimingItemForm(forms.Form):
    reclaiming_material = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'material_suggestions'
        }),
        required=False
    )
    reclaiming_equipment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'reclaiming_equipment_suggestions'
        }),
        required=False
    )
    reclaiming_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False
    )


# Form for individual feeding items in batch entry
class FeedingItemForm(forms.Form):
    feeding_material = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'material_suggestions'
        }),
        required=False
    )
    feeding_equipment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'feeding_equipment_suggestions'
        }),
        required=False
    )
    feeding_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False
    )


# Form for individual receiving items in batch entry
class ReceivingItemForm(forms.Form):
    receiving_material = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'material_suggestions'
        }),
        required=False
    )
    receiving_equipment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'receiving_equipment_suggestions'
        }),
        required=False
    )
    receiving_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False
    )


# Form for individual crushing items in batch entry
class CrushingItemForm(forms.Form):
    crushing_material = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'material_suggestions'
        }),
        required=False
    )
    crushing_equipment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'crushing_equipment_suggestions'
        }),
        required=False
    )
    crushing_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False
    )


# Form for individual base mix items in batch entry
class BaseMixItemForm(forms.Form):
    base_mix_material = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'material_suggestions'
        }),
        required=False
    )
    base_mix_equipment = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'base_mix_equipment_suggestions'
        }),
        required=False
    )
    base_mix_quantity = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        required=False
    )


class Area1OperationForm(forms.ModelForm):
    """Form for Area-1 operations"""
    
    # Extra fields for "Other" options
    reclaiming_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    feeding_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    receiving_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reclaiming_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    feeding_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    receiving_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Area1Operation
        fields = [
            'date', 'shift',
            'reclaiming_material', 'reclaiming_quantity', 'reclaiming_equipment',
            'feeding_destination', 'feeding_material', 'feeding_quantity', 'feeding_equipment',
            'receiving_source', 'receiving_material', 'receiving_quantity', 'receiving_equipment',
            'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift': forms.Select(attrs={'class': 'form-control select2'}),
            
            'reclaiming_material': forms.Select(attrs={'class': 'form-control select2'}),
            'reclaiming_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'reclaiming_equipment': forms.Select(choices=RECLAIMING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'feeding_destination': forms.Select(choices=DESTINATION_CHOICES, attrs={'class': 'form-control select2'}),
            'feeding_material': forms.Select(attrs={'class': 'form-control select2'}),
            'feeding_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'feeding_equipment': forms.Select(choices=FEEDING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'receiving_source': forms.Select(choices=SOURCE_CHOICES, attrs={'class': 'form-control select2'}),
            'receiving_material': forms.Select(attrs={'class': 'form-control select2'}),
            'receiving_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'receiving_equipment': forms.Select(choices=RECEIVING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set the current date as default
        if not self.instance.pk:
            self.initial['date'] = timezone.now().date()
            
            # Set the current user as the creator
            if user:
                self.instance.created_by = user


class Area23OperationForm(forms.ModelForm):
    """Form for Area-2&3 operations"""
    
    # Extra fields for "Other" options
    feeding_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    receiving_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    crushing_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    base_mix_other_material = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    feeding_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    receiving_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    crushing_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    base_mix_other_equipment = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Area23Operation
        fields = [
            'date', 'shift',
            'feeding_material', 'feeding_quantity', 'feeding_equipment',
            'receiving_material', 'receiving_quantity', 'receiving_equipment',
            'crushing_material', 'crushing_quantity', 'crushing_equipment',
            'base_mix_material', 'base_mix_quantity', 'base_mix_equipment',
            'remarks'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift': forms.Select(attrs={'class': 'form-control select2'}),
            
            'feeding_material': forms.Select(attrs={'class': 'form-control select2'}),
            'feeding_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'feeding_equipment': forms.Select(choices=FEEDING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'receiving_material': forms.Select(attrs={'class': 'form-control select2'}),
            'receiving_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'receiving_equipment': forms.Select(choices=RECEIVING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'crushing_material': forms.Select(attrs={'class': 'form-control select2'}),
            'crushing_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'crushing_equipment': forms.Select(choices=CRUSHING_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'base_mix_material': forms.Select(attrs={'class': 'form-control select2'}),
            'base_mix_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'base_mix_equipment': forms.Select(choices=BASE_MIX_EQUIPMENT_CHOICES, attrs={'class': 'form-control select2'}),
            
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set the current date as default
        if not self.instance.pk:
            self.initial['date'] = timezone.now().date()
            
            # Set the current user as the creator
            if user:
                self.instance.created_by = user


# Create formsets
ReclaimingItemFormFormSet = formset_factory(ReclaimingItemForm, formset=RequiredFormSet, extra=1)
FeedingItemFormFormSet = formset_factory(FeedingItemForm, formset=RequiredFormSet, extra=1)
ReceivingItemFormFormSet = formset_factory(ReceivingItemForm, formset=RequiredFormSet, extra=1)

FeedingFormSet = formset_factory(FeedingItemForm, formset=RequiredFormSet, extra=1)
ReceivingFormSet = formset_factory(ReceivingItemForm, formset=RequiredFormSet, extra=1)
CrushingFormSet = formset_factory(CrushingItemForm, formset=RequiredFormSet, extra=1)
BaseMixFormSet = formset_factory(BaseMixItemForm, formset=RequiredFormSet, extra=1) 