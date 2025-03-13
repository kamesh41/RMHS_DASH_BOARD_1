from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Rake
from .forms import RakeEntryForm

@login_required
def rake_list(request):
    """List view for rakes"""
    # Get filter parameters
    today = timezone.now().date()
    selected_date = request.GET.get('date', '')
    selected_shift = request.GET.get('shift', '')
    selected_material = request.GET.get('material', '')
    selected_status = request.GET.get('status', '')
    
    # Base filters
    filters = {}
    if selected_date:
        filters['date'] = selected_date
    else:
        filters['date'] = today
        selected_date = today
    
    if selected_shift:
        filters['shift'] = selected_shift
    if selected_material:
        filters['material_type'] = selected_material
    if selected_status:
        filters['status'] = selected_status
    
    # Get rakes data
    rakes = Rake.objects.filter(**filters).order_by('-date', '-created_at')
    
    context = {
        'rakes': rakes,
        'selected_date': selected_date,
        'selected_shift': selected_shift,
        'selected_material': selected_material,
        'selected_status': selected_status,
    }
    
    return render(request, 'rakes/rake_list.html', context)

@login_required
def rake_create(request):
    """Create view for rakes"""
    if request.method == 'POST':
        form = RakeEntryForm(request.POST, user=request.user)
        if form.is_valid():
            rake = form.save()
            messages.success(request, 'Rake report created successfully.')
            return redirect('rakes:detail', pk=rake.pk)
    else:
        form = RakeEntryForm(user=request.user)
    
    return render(request, 'rakes/rake_form.html', {'form': form, 'is_creating': True})

@login_required
def rake_detail(request, pk):
    """Detail view for rakes"""
    rake = get_object_or_404(Rake, pk=pk)
    return render(request, 'rakes/rake_detail.html', {'rake': rake})

@login_required
def rake_update(request, pk):
    """Update view for rakes"""
    rake = get_object_or_404(Rake, pk=pk)
    
    if request.method == 'POST':
        form = RakeEntryForm(request.POST, instance=rake, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rake report updated successfully.')
            return redirect('rakes:detail', pk=rake.pk)
    else:
        form = RakeEntryForm(instance=rake, user=request.user)
    
    return render(request, 'rakes/rake_form.html', {'form': form, 'rake': rake, 'is_creating': False})

@login_required
def rake_delete(request, pk):
    """Delete view for rakes"""
    rake = get_object_or_404(Rake, pk=pk)
    if request.method == 'POST':
        rake.delete()
        messages.success(request, 'Rake report deleted successfully.')
        return redirect('rakes:list')
    return render(request, 'rakes/rake_confirm_delete.html', {'rake': rake})

@login_required
def rake_complete(request, pk):
    """Mark a rake as completed"""
    rake = get_object_or_404(Rake, pk=pk)
    if request.method == 'POST':
        rake.status = 'COMPLETED'
        rake.unloading_end_time = timezone.now()
        rake.save()
        messages.success(request, 'Rake marked as completed.')
        return redirect('rakes:detail', pk=rake.pk)
    return render(request, 'rakes/rake_complete.html', {'rake': rake}) 