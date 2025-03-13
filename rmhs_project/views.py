from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from operations.models import Area1Operation, Area23Operation
from delays.models import Delay
from rakes.models import Rake
from maintenance.models import MaintenanceActivity

@login_required
def dashboard(request):
    """Main dashboard view showing summary of all activities"""
    # Get filter parameters
    selected_date = request.GET.get('date', timezone.now().date())
    selected_shift = request.GET.get('shift', '')
    
    # Base filters
    date_filter = {'date': selected_date}
    if selected_shift:
        date_filter['shift'] = selected_shift
    
    # Get operations data
    area1_operations = Area1Operation.objects.filter(**date_filter)
    area23_operations = Area23Operation.objects.filter(**date_filter)
    
    # Calculate totals with proper None handling
    area1_feeding = area1_operations.aggregate(total=Sum('feeding_quantity'))['total'] or 0
    area23_feeding = area23_operations.aggregate(total=Sum('feeding_quantity'))['total'] or 0
    total_feeding = float(area1_feeding + area23_feeding)
    
    area1_receiving = area1_operations.aggregate(total=Sum('receiving_quantity'))['total'] or 0
    area23_receiving = area23_operations.aggregate(total=Sum('receiving_quantity'))['total'] or 0
    total_receiving = float(area1_receiving + area23_receiving)
    
    total_crushing = float(area23_operations.aggregate(total=Sum('crushing_quantity'))['total'] or 0)
    total_reclaiming = float(area1_operations.aggregate(total=Sum('reclaiming_quantity'))['total'] or 0)
    
    # Material-specific data (these would typically come from more detailed models)
    # For now, we'll estimate based on the total values
    
    # Base Mix data (from Area23Operation)
    base_mix_feeding = float(area23_operations.aggregate(total=Sum('base_mix_quantity'))['total'] or 0)
    base_mix_receiving = base_mix_feeding * 0.9  # Estimate
    base_mix_crushing = base_mix_feeding * 0.1   # Estimate
    base_mix_reclaiming = base_mix_feeding * 0.8  # Estimate
    
    # Coke data (estimated)
    coke_feeding = total_feeding * 0.15
    coke_receiving = total_receiving * 0.15
    coke_crushing = total_crushing * 0.25
    coke_reclaiming = total_reclaiming * 0.1
    
    # Coal data (estimated)
    coal_feeding = total_feeding * 0.2
    coal_receiving = total_receiving * 0.2
    coal_crushing = total_crushing * 0.3
    coal_reclaiming = total_reclaiming * 0.15
    
    # Sinter data (estimated)
    sinter_feeding = total_feeding * 0.25
    sinter_receiving = total_receiving * 0.25
    sinter_crushing = total_crushing * 0.1
    sinter_reclaiming = total_reclaiming * 0.3
    
    # Limestone data (estimated)
    limestone_feeding = total_feeding * 0.1
    limestone_receiving = total_receiving * 0.1
    limestone_crushing = total_crushing * 0.15
    limestone_reclaiming = total_reclaiming * 0.1
    
    # Iron Ore data (estimated)
    iron_ore_feeding = total_feeding * 0.2
    iron_ore_receiving = total_receiving * 0.2
    iron_ore_crushing = total_crushing * 0.1
    iron_ore_reclaiming = total_reclaiming * 0.25
    
    # Dolomite data (estimated)
    dolomite_feeding = total_feeding * 0.1
    dolomite_receiving = total_receiving * 0.1
    dolomite_crushing = total_crushing * 0.1
    dolomite_reclaiming = total_reclaiming * 0.1
    
    # Get delays data
    delays = Delay.objects.filter(**date_filter)
    mechanical_delays = float(delays.filter(delay_type='MECHANICAL').aggregate(total=Sum('duration_hours'))['total'] or 0)
    electrical_delays = float(delays.filter(delay_type='ELECTRICAL').aggregate(total=Sum('duration_hours'))['total'] or 0)
    operational_delays = float(delays.filter(delay_type='OPERATIONAL').aggregate(total=Sum('duration_hours'))['total'] or 0)
    
    # Get rakes data
    rakes = Rake.objects.filter(**date_filter)
    total_rakes = rakes.count()
    completed_rakes = rakes.filter(status='COMPLETED').count()
    rake_percentage = (completed_rakes / total_rakes * 100) if total_rakes > 0 else 0
    
    # Get maintenance data
    maintenance_activities = MaintenanceActivity.objects.filter(**date_filter)
    maintenance_count = maintenance_activities.count()
    
    # Target values (these would typically come from a settings model)
    target_feeding = 5000  # Example target in MT
    target_receiving = 4000  # Example target in MT
    target_crushing = 3000  # Example target in MT
    target_reclaiming = 2500  # Example target in MT
    
    context = {
        'selected_date': selected_date,
        'selected_shift': selected_shift,
        
        # Operations data
        'total_feeding': total_feeding,
        'total_receiving': total_receiving,
        'total_crushing': total_crushing,
        'total_reclaiming': total_reclaiming,
        
        # Material-specific data
        'base_mix_feeding': base_mix_feeding,
        'base_mix_receiving': base_mix_receiving,
        'base_mix_crushing': base_mix_crushing,
        'base_mix_reclaiming': base_mix_reclaiming,
        
        'coke_feeding': coke_feeding,
        'coke_receiving': coke_receiving,
        'coke_crushing': coke_crushing,
        'coke_reclaiming': coke_reclaiming,
        
        'coal_feeding': coal_feeding,
        'coal_receiving': coal_receiving,
        'coal_crushing': coal_crushing,
        'coal_reclaiming': coal_reclaiming,
        
        'sinter_feeding': sinter_feeding,
        'sinter_receiving': sinter_receiving,
        'sinter_crushing': sinter_crushing,
        'sinter_reclaiming': sinter_reclaiming,
        
        'limestone_feeding': limestone_feeding,
        'limestone_receiving': limestone_receiving,
        'limestone_crushing': limestone_crushing,
        'limestone_reclaiming': limestone_reclaiming,
        
        'iron_ore_feeding': iron_ore_feeding,
        'iron_ore_receiving': iron_ore_receiving,
        'iron_ore_crushing': iron_ore_crushing,
        'iron_ore_reclaiming': iron_ore_reclaiming,
        
        'dolomite_feeding': dolomite_feeding,
        'dolomite_receiving': dolomite_receiving,
        'dolomite_crushing': dolomite_crushing,
        'dolomite_reclaiming': dolomite_reclaiming,
        
        # Target values
        'target_feeding': target_feeding,
        'target_receiving': target_receiving,
        'target_crushing': target_crushing,
        'target_reclaiming': target_reclaiming,
        
        # Delays data
        'mechanical_delays': mechanical_delays,
        'electrical_delays': electrical_delays,
        'operational_delays': operational_delays,
        
        # Rakes data
        'total_rakes': total_rakes,
        'completed_rakes': completed_rakes,
        'rake_percentage': rake_percentage,
        
        # Maintenance data
        'maintenance_count': maintenance_count,
    }
    
    return render(request, 'dashboard/index.html', context) 