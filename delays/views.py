from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Delay
from .forms import DelayReportForm

@login_required
def delay_list(request):
    """List view for delays"""
    # Get filter parameters
    today = timezone.now().date()
    selected_date = request.GET.get('date', '')
    selected_shift = request.GET.get('shift', '')
    selected_type = request.GET.get('type', '')
    selected_area = request.GET.get('area', '')
    selected_resolved = request.GET.get('resolved', '')
    
    # Base filters
    filters = {}
    if selected_date:
        filters['date'] = selected_date
    else:
        filters['date'] = today
        selected_date = today
    
    if selected_shift:
        filters['shift'] = selected_shift
    if selected_type:
        filters['delay_type'] = selected_type
    if selected_area:
        filters['area'] = selected_area
    if selected_resolved:
        filters['is_resolved'] = selected_resolved == 'true'
    
    # Get delays data
    delays = Delay.objects.filter(**filters).order_by('-date', '-created_at')
    
    # Calculate delay statistics
    mechanical_delays = sum([delay.duration_hours for delay in delays.filter(delay_type='MECHANICAL')])
    electrical_delays = sum([delay.duration_hours for delay in delays.filter(delay_type='ELECTRICAL')])
    operational_delays = sum([delay.duration_hours for delay in delays.filter(delay_type='OPERATIONAL')])
    
    total_delays = mechanical_delays + electrical_delays + operational_delays
    
    # Calculate percentages for progress bars
    if total_delays > 0:
        mechanical_percentage = (mechanical_delays / total_delays) * 100
        electrical_percentage = (electrical_delays / total_delays) * 100
        operational_percentage = (operational_delays / total_delays) * 100
    else:
        mechanical_percentage = electrical_percentage = operational_percentage = 0
    
    context = {
        'delays': delays,
        'selected_date': selected_date,
        'selected_shift': selected_shift,
        'selected_type': selected_type,
        'selected_area': selected_area,
        'selected_resolved': selected_resolved,
        'mechanical_delays': mechanical_delays,
        'electrical_delays': electrical_delays,
        'operational_delays': operational_delays,
        'total_delays': total_delays,
        'mechanical_percentage': mechanical_percentage,
        'electrical_percentage': electrical_percentage,
        'operational_percentage': operational_percentage,
    }
    
    return render(request, 'delays/delay_list.html', context)

@login_required
def delay_create(request):
    """Create view for delays"""
    if request.method == 'POST':
        form = DelayReportForm(request.POST, user=request.user)
        if form.is_valid():
            delay = form.save()
            messages.success(request, 'Delay report created successfully.')
            return redirect('delays:detail', pk=delay.pk)
    else:
        form = DelayReportForm(user=request.user)
    
    return render(request, 'delays/delay_form.html', {'form': form, 'is_creating': True})

@login_required
def delay_detail(request, pk):
    """Detail view for delays"""
    delay = get_object_or_404(Delay, pk=pk)
    return render(request, 'delays/delay_detail.html', {'delay': delay})

@login_required
def delay_update(request, pk):
    """Update view for delays"""
    delay = get_object_or_404(Delay, pk=pk)
    
    if request.method == 'POST':
        form = DelayReportForm(request.POST, instance=delay, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Delay report updated successfully.')
            return redirect('delays:detail', pk=delay.pk)
    else:
        form = DelayReportForm(instance=delay, user=request.user)
    
    return render(request, 'delays/delay_form.html', {'form': form, 'delay': delay, 'is_creating': False})

@login_required
def delay_delete(request, pk):
    """Delete view for delays"""
    delay = get_object_or_404(Delay, pk=pk)
    if request.method == 'POST':
        delay.delete()
        messages.success(request, 'Delay report deleted successfully.')
        return redirect('delays:list')
    return render(request, 'delays/delay_confirm_delete.html', {'delay': delay})

@login_required
def delay_resolve(request, pk):
    """Resolve a delay"""
    delay = get_object_or_404(Delay, pk=pk)
    if request.method == 'POST':
        delay.is_resolved = True
        delay.resolution_time = timezone.now()
        delay.save()
        messages.success(request, 'Delay marked as resolved.')
        return redirect('delays:detail', pk=delay.pk)
    return render(request, 'delays/delay_resolve.html', {'delay': delay}) 