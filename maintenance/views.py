from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import MaintenanceActivity, Spare
from .forms import MaintenancePlanningForm, MaintenanceExecutionForm, SpareForm

@login_required
def maintenance_list(request):
    """List view for maintenance activities"""
    # Get filter parameters
    today = timezone.now().date()
    selected_date = request.GET.get('date', '')
    selected_type = request.GET.get('type', '')
    selected_category = request.GET.get('category', '')
    selected_activity_type = request.GET.get('activity_type', '')
    
    # Base filters
    filters = {}
    if selected_date:
        filters['date'] = selected_date
    else:
        filters['date'] = today
        selected_date = today
    
    # Always filter for General Shift since maintenance only happens in general shift
    filters['shift'] = 'G'
    
    if selected_type:
        filters['maintenance_type'] = selected_type
    if selected_category:
        filters['maintenance_category'] = selected_category
    if selected_activity_type:
        filters['activity_type'] = selected_activity_type
    
    # Get maintenance data
    activities = MaintenanceActivity.objects.filter(**filters).order_by('-date', '-created_at')
    
    # Separate planning and execution activities
    planning_activities = activities.filter(activity_type='PLANNED')
    execution_activities = activities.filter(activity_type='EXECUTION')
    
    context = {
        'activities': activities,
        'planning_activities': planning_activities,
        'execution_activities': execution_activities,
        'selected_date': selected_date,
        'selected_type': selected_type,
        'selected_category': selected_category,
        'selected_activity_type': selected_activity_type,
    }
    
    return render(request, 'maintenance/maintenance_list.html', context)

@login_required
def maintenance_create_plan(request):
    """Create view for planning maintenance activities (morning entry)"""
    if request.method == 'POST':
        form = MaintenancePlanningForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            messages.success(request, 'Maintenance plan created successfully.')
            return redirect('maintenance:detail', pk=activity.pk)
    else:
        form = MaintenancePlanningForm()
    
    return render(request, 'maintenance/maintenance_plan_form.html', {'form': form})

@login_required
def maintenance_create_execution(request, plan_pk=None):
    """Create view for execution of maintenance activities (evening entry)"""
    planning_activity = None
    if plan_pk:
        planning_activity = get_object_or_404(MaintenanceActivity, pk=plan_pk, activity_type='PLANNED')
    
    if request.method == 'POST':
        form = MaintenanceExecutionForm(request.POST, planning_activity=planning_activity)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            
            # Mark the planning activity as completed if needed
            if planning_activity and activity.is_completed:
                planning_activity.is_completed = True
                planning_activity.completion_time = timezone.now()
                planning_activity.save()
            
            messages.success(request, 'Maintenance execution report created successfully.')
            return redirect('maintenance:detail', pk=activity.pk)
    else:
        form = MaintenanceExecutionForm(planning_activity=planning_activity)
    
    context = {
        'form': form,
        'planning_activity': planning_activity
    }
    return render(request, 'maintenance/maintenance_execution_form.html', context)

@login_required
def maintenance_detail(request, pk):
    """Detail view for maintenance activities"""
    activity = get_object_or_404(MaintenanceActivity, pk=pk)
    
    # Get related activities
    related_activities = []
    if activity.activity_type == 'PLANNED':
        related_activities = activity.execution_reports.all()
    elif activity.related_activity:
        related_activities = [activity.related_activity]
    
    context = {
        'activity': activity,
        'related_activities': related_activities
    }
    return render(request, 'maintenance/maintenance_detail.html', context)

@login_required
def maintenance_update(request, pk):
    """Update view for maintenance activities"""
    activity = get_object_or_404(MaintenanceActivity, pk=pk)
    
    if activity.activity_type == 'PLANNED':
        if request.method == 'POST':
            form = MaintenancePlanningForm(request.POST, instance=activity)
            if form.is_valid():
                form.save()
                messages.success(request, 'Maintenance plan updated successfully.')
                return redirect('maintenance:detail', pk=activity.pk)
        else:
            form = MaintenancePlanningForm(instance=activity)
        template = 'maintenance/maintenance_plan_form.html'
    else:
        # It's an execution activity
        if request.method == 'POST':
            form = MaintenanceExecutionForm(request.POST, instance=activity)
            if form.is_valid():
                form.save()
                messages.success(request, 'Maintenance execution report updated successfully.')
                return redirect('maintenance:detail', pk=activity.pk)
        else:
            form = MaintenanceExecutionForm(instance=activity)
        template = 'maintenance/maintenance_execution_form.html'
    
    return render(request, template, {'form': form, 'activity': activity})

@login_required
def maintenance_delete(request, pk):
    """Delete view for maintenance activities"""
    activity = get_object_or_404(MaintenanceActivity, pk=pk)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Maintenance activity deleted successfully.')
        return redirect('maintenance:list')
    return render(request, 'maintenance/maintenance_confirm_delete.html', {'activity': activity})

@login_required
def maintenance_complete(request, pk):
    """Mark a maintenance activity as completed"""
    activity = get_object_or_404(MaintenanceActivity, pk=pk)
    if request.method == 'POST':
        activity.is_completed = True
        activity.completion_time = timezone.now()
        activity.save()
        messages.success(request, 'Maintenance activity marked as completed.')
        return redirect('maintenance:detail', pk=activity.pk)
    return render(request, 'maintenance/maintenance_complete.html', {'activity': activity})

@login_required
def pending_activities(request):
    """View for displaying all pending maintenance activities"""
    # Get activities that are not completed
    activities = MaintenanceActivity.objects.filter(is_completed=False).order_by('-priority', 'date')
    
    # Filter by type if requested
    maintenance_type = request.GET.get('type', '')
    if maintenance_type:
        activities = activities.filter(maintenance_type=maintenance_type)
    
    context = {
        'activities': activities,
        'selected_type': maintenance_type
    }
    return render(request, 'maintenance/pending_activities.html', context)

@login_required
def spare_list(request):
    """List view for spare parts"""
    # Filter by maintenance type if requested
    maintenance_type = request.GET.get('type', '')
    
    # Base query
    spares = Spare.objects.all().order_by('name')
    
    if maintenance_type:
        spares = spares.filter(maintenance_type=maintenance_type)
    
    # Highlight low stock items
    low_stock_spares = [spare for spare in spares if spare.is_low_stock]
    
    context = {
        'spares': spares,
        'low_stock_spares': low_stock_spares,
        'selected_type': maintenance_type
    }
    return render(request, 'maintenance/spare_list.html', context)

@login_required
def spare_detail(request, pk):
    """Detail view for spare parts"""
    spare = get_object_or_404(Spare, pk=pk)
    return render(request, 'maintenance/spare_detail.html', {'spare': spare})

@login_required
def spare_create(request):
    """Create view for spare parts"""
    if request.method == 'POST':
        form = SpareForm(request.POST)
        if form.is_valid():
            spare = form.save()
            messages.success(request, 'Spare part added successfully.')
            return redirect('maintenance:spare_detail', pk=spare.pk)
    else:
        form = SpareForm()
    
    return render(request, 'maintenance/spare_form.html', {'form': form})

@login_required
def spare_update(request, pk):
    """Update view for spare parts"""
    spare = get_object_or_404(Spare, pk=pk)
    if request.method == 'POST':
        form = SpareForm(request.POST, instance=spare)
        if form.is_valid():
            form.save()
            messages.success(request, 'Spare part updated successfully.')
            return redirect('maintenance:spare_detail', pk=spare.pk)
    else:
        form = SpareForm(instance=spare)
    
    return render(request, 'maintenance/spare_form.html', {'form': form, 'spare': spare})

@login_required
def spare_delete(request, pk):
    """Delete view for spare parts"""
    spare = get_object_or_404(Spare, pk=pk)
    if request.method == 'POST':
        spare.delete()
        messages.success(request, 'Spare part deleted successfully.')
        return redirect('maintenance:spare_list')
    return render(request, 'maintenance/spare_confirm_delete.html', {'spare': spare}) 