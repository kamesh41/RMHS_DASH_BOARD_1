from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count
from django.core.paginator import Paginator
import json
import csv
from datetime import datetime, timedelta
from django.urls import reverse

from .models import Area1Operation, Area23Operation, MATERIAL_CHOICES, SHIFT_CHOICES
from .forms import (
    Area1OperationForm, Area23OperationForm,
    Area1BatchEntryForm, Area23BatchEntryForm,
    ReclaimingItemForm, FeedingItemForm, ReceivingItemForm,
    CrushingItemForm, BaseMixItemForm,
    ReclaimingItemFormFormSet, FeedingItemFormFormSet, ReceivingItemFormFormSet,
    FeedingFormSet, ReceivingFormSet, CrushingFormSet, BaseMixFormSet,
    RECLAIMING_EQUIPMENT_CHOICES, FEEDING_EQUIPMENT_CHOICES, RECEIVING_EQUIPMENT_CHOICES,
    CRUSHING_EQUIPMENT_CHOICES, BASE_MIX_EQUIPMENT_CHOICES
)
from .constants import EQUIPMENT_PRESETS

@login_required
def area1_list(request):
    """List view for Area-1 operations"""
    # Get filter parameters
    selected_date = request.GET.get('date')
    selected_shift = request.GET.get('shift')
    
    # Parse date if provided
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    # Filter operations
    operations = Area1Operation.objects.filter(date=selected_date)
    if selected_shift:
        operations = operations.filter(shift=selected_shift)
    
    # Calculate aggregated summaries
    reclaiming_summary = operations.values(
        'reclaiming_material', 'reclaiming_other_material'
    ).annotate(
        total_quantity=Sum('reclaiming_quantity')
    ).filter(total_quantity__gt=0).order_by('-total_quantity')
    
    feeding_summary = operations.values(
        'feeding_material', 'feeding_other_material'
    ).annotate(
        total_quantity=Sum('feeding_quantity')
    ).filter(total_quantity__gt=0).order_by('-total_quantity')
    
    receiving_summary = operations.values(
        'receiving_material', 'receiving_other_material'
    ).annotate(
        total_quantity=Sum('receiving_quantity')
    ).filter(total_quantity__gt=0).order_by('-total_quantity')
    
    # Calculate totals
    reclaiming_total = sum(item['total_quantity'] or 0 for item in reclaiming_summary)
    feeding_total = sum(item['total_quantity'] or 0 for item in feeding_summary)
    receiving_total = sum(item['total_quantity'] or 0 for item in receiving_summary)
    
    context = {
        'operations': operations,
        'selected_date': selected_date,
        'selected_shift': selected_shift,
        'material_choices': MATERIAL_CHOICES,
        'shift_choices': SHIFT_CHOICES,
        'reclaiming_summary': reclaiming_summary,
        'feeding_summary': feeding_summary,
        'receiving_summary': receiving_summary,
        'reclaiming_total': reclaiming_total,
        'feeding_total': feeding_total,
        'receiving_total': receiving_total,
    }
    
    # Add cache control headers to prevent browser caching
    response = render(request, 'operations/area1_list.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def area1_create(request):
    """Create view for Area-1 operations"""
    if request.method == 'POST':
        form = Area1OperationForm(request.POST, user=request.user)
        if form.is_valid():
            operation = form.save()
            messages.success(request, 'Area-1 operation entry created successfully.')
            return redirect('operations:area1_detail', pk=operation.pk)
    else:
        form = Area1OperationForm(user=request.user)
    
    return render(request, 'operations/area1_form.html', {'form': form})

@login_required
def area1_batch_entry(request):
    """View for batch entry of Area-1 operations"""
    if request.method == 'POST':
        # Process the form submission
        batch_form = Area1BatchEntryForm(request.POST)
        reclaiming_formset = ReclaimingItemFormFormSet(request.POST, prefix='reclaiming_formset')
        feeding_formset = FeedingItemFormFormSet(request.POST, prefix='feeding_formset')
        receiving_formset = ReceivingItemFormFormSet(request.POST, prefix='receiving_formset')
        
        # Debug information
        if not reclaiming_formset.is_valid():
            print(f"Reclaiming form errors: {[form.errors for form in reclaiming_formset]}")
        if not feeding_formset.is_valid():
            print(f"Feeding form errors: {[form.errors for form in feeding_formset]}")
        if not receiving_formset.is_valid():
            print(f"Receiving form errors: {[form.errors for form in receiving_formset]}")
        
        # Check if the form is valid
        if batch_form.is_valid() and (reclaiming_formset.is_valid() or feeding_formset.is_valid() or receiving_formset.is_valid()):
            # Get common data from the batch form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data['remarks']
            
            # Process valid entries
            entries_created = 0
            
            # Process reclaiming forms
            for form in reclaiming_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('reclaiming_material')
                    equipment = form.cleaned_data.get('reclaiming_equipment')
                    quantity = form.cleaned_data.get('reclaiming_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area1Operation for reclaiming
                        Area1Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            reclaiming_material=material,
                            reclaiming_equipment=equipment,
                            reclaiming_quantity=quantity
                        )
                        entries_created += 1
            
            # Process feeding forms
            for form in feeding_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('feeding_material')
                    equipment = form.cleaned_data.get('feeding_equipment')
                    quantity = form.cleaned_data.get('feeding_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area1Operation for feeding
                        Area1Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            feeding_material=material,
                            feeding_equipment=equipment,
                            feeding_quantity=quantity
                        )
                        entries_created += 1
            
            # Process receiving forms
            for form in receiving_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('receiving_material')
                    equipment = form.cleaned_data.get('receiving_equipment')
                    quantity = form.cleaned_data.get('receiving_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area1Operation for receiving
                        Area1Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            receiving_material=material,
                            receiving_equipment=equipment,
                            receiving_quantity=quantity
                        )
                        entries_created += 1
            
            if entries_created > 0:
                messages.success(request, f'Successfully created {entries_created} entries.')
            else:
                messages.warning(request, 'No valid entries were found to create.')
            
            # Redirect to the list view with date and shift parameters
            return redirect(f'/operations/area1/list/?date={date}&shift={shift}')
    else:
        # Initialize the forms
        batch_form = Area1BatchEntryForm()
        reclaiming_formset = ReclaimingItemFormFormSet(prefix='reclaiming_formset')
        feeding_formset = FeedingItemFormFormSet(prefix='feeding_formset')
        receiving_formset = ReceivingItemFormFormSet(prefix='receiving_formset')
    
    # Prepare context for rendering the template
    context = {
        'batch_form': batch_form,
        'reclaiming_formset': reclaiming_formset,
        'feeding_formset': feeding_formset,
        'receiving_formset': receiving_formset,
        'material_choices': MATERIAL_CHOICES,
        'reclaiming_equipment_choices': RECLAIMING_EQUIPMENT_CHOICES,
        'feeding_equipment_choices': FEEDING_EQUIPMENT_CHOICES,
        'receiving_equipment_choices': RECEIVING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area1_batch_entry.html', context)

@login_required
def area1_detail(request, pk):
    """Detail view for Area-1 operations"""
    operation = get_object_or_404(Area1Operation, pk=pk)
    return render(request, 'operations/area1_detail.html', {'operation': operation})

@login_required
def area1_update(request, pk):
    """Update view for Area-1 operations"""
    operation = get_object_or_404(Area1Operation, pk=pk)
    if request.method == 'POST':
        form = Area1OperationForm(request.POST, instance=operation, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Area-1 operation entry updated successfully.')
            return redirect('operations:area1_detail', pk=operation.pk)
    else:
        form = Area1OperationForm(instance=operation, user=request.user)
    
    return render(request, 'operations/area1_form.html', {'form': form, 'operation': operation})

@login_required
def area1_delete(request, pk):
    """Delete view for Area-1 operations"""
    operation = get_object_or_404(Area1Operation, pk=pk)
    if request.method == 'POST':
        operation.delete()
        messages.success(request, 'Area-1 operation entry deleted successfully.')
        return redirect('operations:area1_list')
    return render(request, 'operations/area1_confirm_delete.html', {'operation': operation})

@login_required
def area23_list(request):
    """List view for Area-2 & 3 operations"""
    # Get filter parameters
    today = timezone.now().date()
    selected_date = request.GET.get('date', '')
    selected_shift = request.GET.get('shift', '')
    
    # Base filters
    filters = {}
    if selected_date:
        filters['date'] = selected_date
    else:
        filters['date'] = today
        selected_date = today
    
    if selected_shift:
        filters['shift'] = selected_shift
    
    # Get operations data
    operations = Area23Operation.objects.filter(**filters).order_by('-date', '-created_at')
    
    # Calculate aggregated totals for summary display
    from django.db.models import Sum, Count
    from .models import MATERIAL_CHOICES, SHIFT_CHOICES
    
    # Get feeding summaries
    feeding_summary = operations.exclude(feeding_material='').values(
        'feeding_material', 'feeding_other_material'
    ).annotate(
        total_quantity=Sum('feeding_quantity'),
        count=Count('id')
    ).order_by('-total_quantity')
    
    # Get receiving summaries
    receiving_summary = operations.exclude(receiving_material='').values(
        'receiving_material', 'receiving_other_material'
    ).annotate(
        total_quantity=Sum('receiving_quantity'),
        count=Count('id')
    ).order_by('-total_quantity')
    
    # Get crushing summaries
    crushing_summary = operations.exclude(crushing_material='').values(
        'crushing_material', 'crushing_other_material'
    ).annotate(
        total_quantity=Sum('crushing_quantity'),
        count=Count('id')
    ).order_by('-total_quantity')
    
    # Get base mix summaries
    base_mix_summary = operations.exclude(base_mix_material='').values(
        'base_mix_material', 'base_mix_other_material'
    ).annotate(
        total_quantity=Sum('base_mix_quantity'),
        count=Count('id')
    ).order_by('-total_quantity')
    
    # Overall totals
    feeding_total = operations.aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0
    receiving_total = operations.aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0
    crushing_total = operations.aggregate(Sum('crushing_quantity'))['crushing_quantity__sum'] or 0
    base_mix_total = operations.aggregate(Sum('base_mix_quantity'))['base_mix_quantity__sum'] or 0
    
    context = {
        'operations': operations,
        'selected_date': selected_date,
        'selected_shift': selected_shift,
        'feeding_summary': feeding_summary,
        'receiving_summary': receiving_summary,
        'crushing_summary': crushing_summary,
        'base_mix_summary': base_mix_summary,
        'feeding_total': feeding_total,
        'receiving_total': receiving_total,
        'crushing_total': crushing_total,
        'base_mix_total': base_mix_total,
        'material_choices': MATERIAL_CHOICES,
        'shift_choices': SHIFT_CHOICES,
    }
    
    # Add cache control headers to prevent browser caching
    response = render(request, 'operations/area23_list.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def area23_create(request):
    """Create view for Area-2 & 3 operations"""
    if request.method == 'POST':
        form = Area23OperationForm(request.POST, user=request.user)
        if form.is_valid():
            operation = form.save()
            messages.success(request, 'Area-2 & 3 operation entry created successfully.')
            return redirect('operations:area23_detail', pk=operation.pk)
    else:
        form = Area23OperationForm(user=request.user)
    
    return render(request, 'operations/area23_form.html', {'form': form})

@login_required
def area23_detail(request, pk):
    """Detail view for Area-2 & 3 operations"""
    operation = get_object_or_404(Area23Operation, pk=pk)
    return render(request, 'operations/area23_detail.html', {'operation': operation})

@login_required
def area23_update(request, pk):
    """Update view for Area-2 & 3 operations"""
    operation = get_object_or_404(Area23Operation, pk=pk)
    if request.method == 'POST':
        form = Area23OperationForm(request.POST, instance=operation, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Area-2 & 3 operation entry updated successfully.')
            return redirect('operations:area23_detail', pk=operation.pk)
    else:
        form = Area23OperationForm(instance=operation, user=request.user)
    
    return render(request, 'operations/area23_form.html', {'form': form, 'operation': operation})

@login_required
def area23_delete(request, pk):
    """Delete view for Area-2 & 3 operations"""
    operation = get_object_or_404(Area23Operation, pk=pk)
    if request.method == 'POST':
        operation.delete()
        messages.success(request, 'Area-2 & 3 operation entry deleted successfully.')
        return redirect('operations:area23_list')
    return render(request, 'operations/area23_confirm_delete.html', {'operation': operation})

@login_required
def area23_batch_entry(request):
    """View for batch entry of Area-2&3 operations"""
    if request.method == 'POST':
        # Process the form submission
        batch_form = Area23BatchEntryForm(request.POST)
        feeding_formset = FeedingFormSet(request.POST, prefix='feeding_formset')
        receiving_formset = ReceivingFormSet(request.POST, prefix='receiving_formset')
        crushing_formset = CrushingFormSet(request.POST, prefix='crushing_formset')
        base_mix_formset = BaseMixFormSet(request.POST, prefix='base_mix_formset')
        
        # Debug information
        if not feeding_formset.is_valid():
            print(f"Feeding form errors: {[form.errors for form in feeding_formset]}")
        if not receiving_formset.is_valid():
            print(f"Receiving form errors: {[form.errors for form in receiving_formset]}")
        if not crushing_formset.is_valid():
            print(f"Crushing form errors: {[form.errors for form in crushing_formset]}")
        if not base_mix_formset.is_valid():
            print(f"Base Mix form errors: {[form.errors for form in base_mix_formset]}")
        
        # Check if the form is valid
        if batch_form.is_valid() and (feeding_formset.is_valid() or receiving_formset.is_valid() or 
                                      crushing_formset.is_valid() or base_mix_formset.is_valid()):
            # Get common data from the batch form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data['remarks']
            
            # Process valid entries
            entries_created = 0
            
            # Process feeding forms
            for form in feeding_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('feeding_material')
                    equipment = form.cleaned_data.get('feeding_equipment')
                    quantity = form.cleaned_data.get('feeding_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area23Operation for feeding
                        Area23Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            feeding_material=material,
                            feeding_equipment=equipment,
                            feeding_quantity=quantity
                        )
                        entries_created += 1
            
            # Process receiving forms
            for form in receiving_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('receiving_material')
                    equipment = form.cleaned_data.get('receiving_equipment')
                    quantity = form.cleaned_data.get('receiving_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area23Operation for receiving
                        Area23Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            receiving_material=material,
                            receiving_equipment=equipment,
                            receiving_quantity=quantity
                        )
                        entries_created += 1
            
            # Process crushing forms
            for form in crushing_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('crushing_material')
                    equipment = form.cleaned_data.get('crushing_equipment')
                    quantity = form.cleaned_data.get('crushing_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area23Operation for crushing
                        Area23Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            crushing_material=material,
                            crushing_equipment=equipment,
                            crushing_quantity=quantity
                        )
                        entries_created += 1
            
            # Process base mix forms
            for form in base_mix_formset:
                if form.is_valid() and form.cleaned_data:
                    material = form.cleaned_data.get('base_mix_material')
                    equipment = form.cleaned_data.get('base_mix_equipment')
                    quantity = form.cleaned_data.get('base_mix_quantity')
                    
                    if material and equipment and quantity:
                        # Create Area23Operation for base mix
                        Area23Operation.objects.create(
                            date=date,
                            shift=shift,
                            remarks=remarks,
                            base_mix_material=material,
                            base_mix_equipment=equipment,
                            base_mix_quantity=quantity
                        )
                        entries_created += 1
            
            if entries_created > 0:
                messages.success(request, f'Successfully created {entries_created} entries.')
            else:
                messages.warning(request, 'No valid entries were found to create.')
            
            # Redirect to the list view with date and shift parameters
            return redirect(f'/operations/area23/list/?date={date}&shift={shift}')
    else:
        # Initialize the forms
        batch_form = Area23BatchEntryForm()
        feeding_formset = FeedingFormSet(prefix='feeding_formset')
        receiving_formset = ReceivingFormSet(prefix='receiving_formset')
        crushing_formset = CrushingFormSet(prefix='crushing_formset')
        base_mix_formset = BaseMixFormSet(prefix='base_mix_formset')
    
    # Prepare context for rendering the template
    context = {
        'batch_form': batch_form,
        'feeding_formset': feeding_formset,
        'receiving_formset': receiving_formset,
        'crushing_formset': crushing_formset,
        'base_mix_formset': base_mix_formset,
        'material_choices': MATERIAL_CHOICES,
        'feeding_equipment_choices': FEEDING_EQUIPMENT_CHOICES,
        'receiving_equipment_choices': RECEIVING_EQUIPMENT_CHOICES,
        'crushing_equipment_choices': CRUSHING_EQUIPMENT_CHOICES,
        'base_mix_equipment_choices': BASE_MIX_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area23_batch_entry.html', context)


# Equipment presets API
@login_required
def equipment_presets(request):
    """API endpoint for equipment presets"""
    return JsonResponse(EQUIPMENT_PRESETS)


# Reports views
@login_required
def operations_report(request):
    """View for operations report by date range"""
    # Default to last 7 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)
    
    # Get filter parameters
    if request.GET:
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid start date format. Using default.')
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid end date format. Using default.')
    
    # Validate date range
    if end_date < start_date:
        messages.error(request, 'End date cannot be earlier than start date. Using default range.')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
    
    # Get data for Area-1
    area1_data = get_area1_report_data(start_date, end_date)
    
    # Get data for Area-2&3
    area23_data = get_area23_report_data(start_date, end_date)
    
    # Prepare context
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'area1_data': area1_data,
        'area23_data': area23_data,
    }
    
    # Handle export requests
    export_format = request.GET.get('export', '')
    if export_format == 'csv':
        return export_report_csv(area1_data, area23_data, start_date, end_date)
    
    return render(request, 'operations/operations_report.html', context)


def get_area1_report_data(start_date, end_date):
    """Get aggregated data for Area-1 operations report"""
    # Base query for date range
    base_query = Area1Operation.objects.filter(date__gte=start_date, date__lte=end_date)
    
    # Get daily totals
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        day_data = {
            'date': current_date,
            'reclaiming_total': base_query.filter(date=current_date).aggregate(Sum('reclaiming_quantity'))['reclaiming_quantity__sum'] or 0,
            'feeding_total': base_query.filter(date=current_date).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(date=current_date).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
        }
        daily_data.append(day_data)
        current_date += timedelta(days=1)
    
    # Get material-wise totals
    material_data = []
    from .models import MATERIAL_CHOICES
    material_dict = dict(MATERIAL_CHOICES)
    
    for material_code, material_name in MATERIAL_CHOICES:
        material_data.append({
            'material': material_name,
            'reclaiming_total': base_query.filter(reclaiming_material=material_code).aggregate(Sum('reclaiming_quantity'))['reclaiming_quantity__sum'] or 0,
            'feeding_total': base_query.filter(feeding_material=material_code).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(receiving_material=material_code).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
        })
    
    # Get shift-wise totals
    shift_data = []
    from .models import SHIFT_CHOICES
    
    for shift_code, shift_name in SHIFT_CHOICES:
        shift_data.append({
            'shift': shift_name,
            'reclaiming_total': base_query.filter(shift=shift_code).aggregate(Sum('reclaiming_quantity'))['reclaiming_quantity__sum'] or 0,
            'feeding_total': base_query.filter(shift=shift_code).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(shift=shift_code).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
        })
    
    # Calculate overall totals
    overall_totals = {
        'reclaiming_total': base_query.aggregate(Sum('reclaiming_quantity'))['reclaiming_quantity__sum'] or 0,
        'feeding_total': base_query.aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
        'receiving_total': base_query.aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
        'entry_count': base_query.count(),
    }
    
    # Calculate efficiency metrics
    efficiency_metrics = {
        'avg_reclaiming_per_day': overall_totals['reclaiming_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
        'avg_feeding_per_day': overall_totals['feeding_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
        'avg_receiving_per_day': overall_totals['receiving_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
    }
    
    return {
        'daily_data': daily_data,
        'material_data': material_data,
        'shift_data': shift_data,
        'overall_totals': overall_totals,
        'efficiency_metrics': efficiency_metrics,
    }


def get_area23_report_data(start_date, end_date):
    """Get aggregated data for Area-2&3 operations report"""
    # Base query for date range
    base_query = Area23Operation.objects.filter(date__gte=start_date, date__lte=end_date)
    
    # Get daily totals
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        day_data = {
            'date': current_date,
            'feeding_total': base_query.filter(date=current_date).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(date=current_date).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
            'crushing_total': base_query.filter(date=current_date).aggregate(Sum('crushing_quantity'))['crushing_quantity__sum'] or 0,
            'base_mix_total': base_query.filter(date=current_date).aggregate(Sum('base_mix_quantity'))['base_mix_quantity__sum'] or 0,
        }
        daily_data.append(day_data)
        current_date += timedelta(days=1)
    
    # Get material-wise totals
    material_data = []
    from .models import MATERIAL_CHOICES
    material_dict = dict(MATERIAL_CHOICES)
    
    for material_code, material_name in MATERIAL_CHOICES:
        material_data.append({
            'material': material_name,
            'feeding_total': base_query.filter(feeding_material=material_code).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(receiving_material=material_code).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
            'crushing_total': base_query.filter(crushing_material=material_code).aggregate(Sum('crushing_quantity'))['crushing_quantity__sum'] or 0,
            'base_mix_total': base_query.filter(base_mix_material=material_code).aggregate(Sum('base_mix_quantity'))['base_mix_quantity__sum'] or 0,
        })
    
    # Get shift-wise totals
    shift_data = []
    from .models import SHIFT_CHOICES
    
    for shift_code, shift_name in SHIFT_CHOICES:
        shift_data.append({
            'shift': shift_name,
            'feeding_total': base_query.filter(shift=shift_code).aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
            'receiving_total': base_query.filter(shift=shift_code).aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
            'crushing_total': base_query.filter(shift=shift_code).aggregate(Sum('crushing_quantity'))['crushing_quantity__sum'] or 0,
            'base_mix_total': base_query.filter(shift=shift_code).aggregate(Sum('base_mix_quantity'))['base_mix_quantity__sum'] or 0,
        })
    
    # Calculate overall totals
    overall_totals = {
        'feeding_total': base_query.aggregate(Sum('feeding_quantity'))['feeding_quantity__sum'] or 0,
        'receiving_total': base_query.aggregate(Sum('receiving_quantity'))['receiving_quantity__sum'] or 0,
        'crushing_total': base_query.aggregate(Sum('crushing_quantity'))['crushing_quantity__sum'] or 0,
        'base_mix_total': base_query.aggregate(Sum('base_mix_quantity'))['base_mix_quantity__sum'] or 0,
        'entry_count': base_query.count(),
    }
    
    # Calculate efficiency metrics
    efficiency_metrics = {
        'avg_feeding_per_day': overall_totals['feeding_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
        'avg_receiving_per_day': overall_totals['receiving_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
        'avg_crushing_per_day': overall_totals['crushing_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
        'avg_base_mix_per_day': overall_totals['base_mix_total'] / ((end_date - start_date).days + 1) if ((end_date - start_date).days + 1) > 0 else 0,
    }
    
    return {
        'daily_data': daily_data,
        'material_data': material_data,
        'shift_data': shift_data,
        'overall_totals': overall_totals,
        'efficiency_metrics': efficiency_metrics,
    }


def export_report_csv(area1_data, area23_data, start_date, end_date):
    """Export operations report data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="operations_report_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['RMHS Operations Report', f'From: {start_date}', f'To: {end_date}'])
    writer.writerow([])
    
    # Write Area-1 data
    writer.writerow(['Area-1 Operations'])
    writer.writerow(['Overall Totals'])
    writer.writerow(['Reclaiming Total (MT)', 'Feeding Total (MT)', 'Receiving Total (MT)', 'Entry Count'])
    writer.writerow([
        area1_data['overall_totals']['reclaiming_total'],
        area1_data['overall_totals']['feeding_total'],
        area1_data['overall_totals']['receiving_total'],
        area1_data['overall_totals']['entry_count']
    ])
    writer.writerow([])
    
    # Write daily data
    writer.writerow(['Daily Totals'])
    writer.writerow(['Date', 'Reclaiming Total (MT)', 'Feeding Total (MT)', 'Receiving Total (MT)'])
    for day in area1_data['daily_data']:
        writer.writerow([
            day['date'],
            day['reclaiming_total'],
            day['feeding_total'],
            day['receiving_total']
        ])
    writer.writerow([])
    
    # Write material-wise data
    writer.writerow(['Material-wise Totals'])
    writer.writerow(['Material', 'Reclaiming Total (MT)', 'Feeding Total (MT)', 'Receiving Total (MT)'])
    for material in area1_data['material_data']:
        writer.writerow([
            material['material'],
            material['reclaiming_total'],
            material['feeding_total'],
            material['receiving_total']
        ])
    writer.writerow([])
    
    # Write Area-2&3 data
    writer.writerow(['Area-2&3 Operations'])
    writer.writerow(['Overall Totals'])
    writer.writerow(['Feeding Total (MT)', 'Receiving Total (MT)', 'Crushing Total (MT)', 'Base Mix Total (MT)', 'Entry Count'])
    writer.writerow([
        area23_data['overall_totals']['feeding_total'],
        area23_data['overall_totals']['receiving_total'],
        area23_data['overall_totals']['crushing_total'],
        area23_data['overall_totals']['base_mix_total'],
        area23_data['overall_totals']['entry_count']
    ])
    writer.writerow([])
    
    # Write daily data
    writer.writerow(['Daily Totals'])
    writer.writerow(['Date', 'Feeding Total (MT)', 'Receiving Total (MT)', 'Crushing Total (MT)', 'Base Mix Total (MT)'])
    for day in area23_data['daily_data']:
        writer.writerow([
            day['date'],
            day['feeding_total'],
            day['receiving_total'],
            day['crushing_total'],
            day['base_mix_total']
        ])
    writer.writerow([])
    
    # Write material-wise data
    writer.writerow(['Material-wise Totals'])
    writer.writerow(['Material', 'Feeding Total (MT)', 'Receiving Total (MT)', 'Crushing Total (MT)', 'Base Mix Total (MT)'])
    for material in area23_data['material_data']:
        writer.writerow([
            material['material'],
            material['feeding_total'],
            material['receiving_total'],
            material['crushing_total'],
            material['base_mix_total']
        ])
    
    return response

@login_required
def area1_landing(request):
    """Landing page for Area-1 operations with navigation to specific operation types"""
    return render(request, 'operations/area1_landing.html')

@login_required
def area1_reclaiming(request):
    """Dedicated form for Area-1 Reclaiming operations"""
    if request.method == 'POST':
        batch_form = Area1BatchEntryForm(request.POST, user=request.user)
        reclaiming_formset = ReclaimingItemFormFormSet(request.POST, prefix='reclaiming_formset')
        
        if batch_form.is_valid() and reclaiming_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in reclaiming_formset:
                if form.cleaned_data and form.cleaned_data.get('reclaiming_material') and form.cleaned_data.get('reclaiming_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one reclaiming operation.')
                return redirect('operations:area1_reclaiming')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in reclaiming_formset:
                if form.cleaned_data and form.cleaned_data.get('reclaiming_material') and form.cleaned_data.get('reclaiming_quantity'):
                    Area1Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        reclaiming_material=form.cleaned_data.get('reclaiming_material'),
                        reclaiming_equipment=form.cleaned_data.get('reclaiming_equipment', ''),
                        reclaiming_quantity=form.cleaned_data.get('reclaiming_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} reclaiming operations.')
            return redirect('operations:area1_summary')
    else:
        batch_form = Area1BatchEntryForm(initial={'date': timezone.now().date()})
        reclaiming_formset = ReclaimingItemFormFormSet(prefix='reclaiming_formset')
    
    context = {
        'batch_form': batch_form,
        'reclaiming_formset': reclaiming_formset,
        'material_choices': MATERIAL_CHOICES,
        'reclaiming_equipment_choices': RECLAIMING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area1_reclaiming.html', context)

@login_required
def area1_feeding(request):
    """Dedicated form for Area-1 Feeding operations"""
    if request.method == 'POST':
        batch_form = Area1BatchEntryForm(request.POST, user=request.user)
        feeding_formset = FeedingItemFormFormSet(request.POST, prefix='feeding_formset')
        
        if batch_form.is_valid() and feeding_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in feeding_formset:
                if form.cleaned_data and form.cleaned_data.get('feeding_material') and form.cleaned_data.get('feeding_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one feeding operation.')
                return redirect('operations:area1_feeding')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in feeding_formset:
                if form.cleaned_data and form.cleaned_data.get('feeding_material') and form.cleaned_data.get('feeding_quantity'):
                    Area1Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        feeding_material=form.cleaned_data.get('feeding_material'),
                        feeding_equipment=form.cleaned_data.get('feeding_equipment', ''),
                        feeding_quantity=form.cleaned_data.get('feeding_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} feeding operations.')
            return redirect('operations:area1_summary')
    else:
        batch_form = Area1BatchEntryForm(initial={'date': timezone.now().date()})
        feeding_formset = FeedingItemFormFormSet(prefix='feeding_formset')
    
    context = {
        'batch_form': batch_form,
        'feeding_formset': feeding_formset,
        'material_choices': MATERIAL_CHOICES,
        'feeding_equipment_choices': FEEDING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area1_feeding.html', context)

@login_required
def area1_receiving(request):
    """Dedicated form for Area-1 Receiving operations"""
    if request.method == 'POST':
        batch_form = Area1BatchEntryForm(request.POST, user=request.user)
        receiving_formset = ReceivingItemFormFormSet(request.POST, prefix='receiving_formset')
        
        if batch_form.is_valid() and receiving_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in receiving_formset:
                if form.cleaned_data and form.cleaned_data.get('receiving_material') and form.cleaned_data.get('receiving_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one receiving operation.')
                return redirect('operations:area1_receiving')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in receiving_formset:
                if form.cleaned_data and form.cleaned_data.get('receiving_material') and form.cleaned_data.get('receiving_quantity'):
                    Area1Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        receiving_material=form.cleaned_data.get('receiving_material'),
                        receiving_equipment=form.cleaned_data.get('receiving_equipment', ''),
                        receiving_quantity=form.cleaned_data.get('receiving_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} receiving operations.')
            return redirect('operations:area1_summary')
    else:
        batch_form = Area1BatchEntryForm(initial={'date': timezone.now().date()})
        receiving_formset = ReceivingItemFormFormSet(prefix='receiving_formset')
    
    context = {
        'batch_form': batch_form,
        'receiving_formset': receiving_formset,
        'material_choices': MATERIAL_CHOICES,
        'receiving_equipment_choices': RECEIVING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area1_receiving.html', context)

@login_required
def area23_landing(request):
    """Landing page for Area-2&3 operations with navigation to specific operation types"""
    return render(request, 'operations/area23_landing.html')

@login_required
def area23_feeding(request):
    """Dedicated form for Area-2&3 Feeding operations"""
    if request.method == 'POST':
        batch_form = Area23BatchEntryForm(request.POST, user=request.user)
        feeding_formset = FeedingFormSet(request.POST, prefix='feeding_formset')
        
        if batch_form.is_valid() and feeding_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in feeding_formset:
                if form.cleaned_data and form.cleaned_data.get('feeding_material') and form.cleaned_data.get('feeding_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one feeding operation.')
                return redirect('operations:area23_feeding')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in feeding_formset:
                if form.cleaned_data and form.cleaned_data.get('feeding_material') and form.cleaned_data.get('feeding_quantity'):
                    Area23Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        feeding_material=form.cleaned_data.get('feeding_material'),
                        feeding_equipment=form.cleaned_data.get('feeding_equipment', ''),
                        feeding_quantity=form.cleaned_data.get('feeding_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} feeding operations.')
            return redirect('operations:area23_summary')
    else:
        batch_form = Area23BatchEntryForm(initial={'date': timezone.now().date()})
        feeding_formset = FeedingFormSet(prefix='feeding_formset')
    
    context = {
        'batch_form': batch_form,
        'feeding_formset': feeding_formset,
        'material_choices': MATERIAL_CHOICES,
        'feeding_equipment_choices': FEEDING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area23_feeding.html', context)

@login_required
def area23_receiving(request):
    """Dedicated form for Area-2&3 Receiving operations"""
    if request.method == 'POST':
        batch_form = Area23BatchEntryForm(request.POST, user=request.user)
        receiving_formset = ReceivingFormSet(request.POST, prefix='receiving_formset')
        
        if batch_form.is_valid() and receiving_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in receiving_formset:
                if form.cleaned_data and form.cleaned_data.get('receiving_material') and form.cleaned_data.get('receiving_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one receiving operation.')
                return redirect('operations:area23_receiving')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in receiving_formset:
                if form.cleaned_data and form.cleaned_data.get('receiving_material') and form.cleaned_data.get('receiving_quantity'):
                    Area23Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        receiving_material=form.cleaned_data.get('receiving_material'),
                        receiving_equipment=form.cleaned_data.get('receiving_equipment', ''),
                        receiving_quantity=form.cleaned_data.get('receiving_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} receiving operations.')
            return redirect('operations:area23_summary')
    else:
        batch_form = Area23BatchEntryForm(initial={'date': timezone.now().date()})
        receiving_formset = ReceivingFormSet(prefix='receiving_formset')
    
    context = {
        'batch_form': batch_form,
        'receiving_formset': receiving_formset,
        'material_choices': MATERIAL_CHOICES,
        'receiving_equipment_choices': RECEIVING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area23_receiving.html', context)

@login_required
def area23_crushing(request):
    """Dedicated form for Area-2&3 Crushing operations"""
    if request.method == 'POST':
        batch_form = Area23BatchEntryForm(request.POST, user=request.user)
        crushing_formset = CrushingFormSet(request.POST, prefix='crushing_formset')
        
        if batch_form.is_valid() and crushing_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in crushing_formset:
                if form.cleaned_data and form.cleaned_data.get('crushing_material') and form.cleaned_data.get('crushing_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one crushing operation.')
                return redirect('operations:area23_crushing')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in crushing_formset:
                if form.cleaned_data and form.cleaned_data.get('crushing_material') and form.cleaned_data.get('crushing_quantity'):
                    Area23Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        crushing_material=form.cleaned_data.get('crushing_material'),
                        crushing_equipment=form.cleaned_data.get('crushing_equipment', ''),
                        crushing_quantity=form.cleaned_data.get('crushing_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} crushing operations.')
            return redirect('operations:area23_summary')
    else:
        batch_form = Area23BatchEntryForm(initial={'date': timezone.now().date()})
        crushing_formset = CrushingFormSet(prefix='crushing_formset')
    
    context = {
        'batch_form': batch_form,
        'crushing_formset': crushing_formset,
        'material_choices': MATERIAL_CHOICES,
        'crushing_equipment_choices': CRUSHING_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area23_crushing.html', context)

@login_required
def area23_base_mix(request):
    """Dedicated form for Area-2&3 Base Mix operations"""
    if request.method == 'POST':
        batch_form = Area23BatchEntryForm(request.POST, user=request.user)
        basemix_formset = BaseMixFormSet(request.POST, prefix='basemix_formset')
        
        if batch_form.is_valid() and basemix_formset.is_valid():
            # Process only if at least one form has data
            has_data = False
            for form in basemix_formset:
                if form.cleaned_data and form.cleaned_data.get('basemix_material') and form.cleaned_data.get('basemix_quantity'):
                    has_data = True
                    break
            
            if not has_data:
                messages.error(request, 'Please enter at least one base mix operation.')
                return redirect('operations:area23_base_mix')
            
            # Create operations for each valid form
            date = batch_form.cleaned_data['date']
            shift = batch_form.cleaned_data['shift']
            remarks = batch_form.cleaned_data.get('remarks', '')
            
            for form in basemix_formset:
                if form.cleaned_data and form.cleaned_data.get('basemix_material') and form.cleaned_data.get('basemix_quantity'):
                    Area23Operation.objects.create(
                        date=date,
                        shift=shift,
                        remarks=remarks,
                        basemix_material=form.cleaned_data.get('basemix_material'),
                        basemix_equipment=form.cleaned_data.get('basemix_equipment', ''),
                        basemix_quantity=form.cleaned_data.get('basemix_quantity'),
                        created_by=request.user,
                        updated_by=request.user
                    )
            
            messages.success(request, f'Successfully added {has_data} base mix operations.')
            return redirect('operations:area23_summary')
    else:
        batch_form = Area23BatchEntryForm(initial={'date': timezone.now().date()})
        basemix_formset = BaseMixFormSet(prefix='basemix_formset')
    
    context = {
        'batch_form': batch_form,
        'basemix_formset': basemix_formset,
        'material_choices': MATERIAL_CHOICES,
        'basemix_equipment_choices': BASE_MIX_EQUIPMENT_CHOICES,
    }
    
    return render(request, 'operations/area23_basemix.html', context) 