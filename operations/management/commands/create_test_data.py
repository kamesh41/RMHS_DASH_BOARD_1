from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from datetime import timedelta
import random

from operations.models import Area1Operation, Area23Operation
from delays.models import Delay
from rakes.models import Rake
from maintenance.models import MaintenanceActivity

class Command(BaseCommand):
    help = 'Creates test data for the RMHS Dashboard'

    def handle(self, *args, **kwargs):
        # Create test user if it doesn't exist
        User = get_user_model()
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'is_staff': True
            }
        )
        if created:
            test_user.set_password('test123')
            test_user.save()
            # Add user to Operations group
            operations_group, _ = Group.objects.get_or_create(name='Operations')
            test_user.groups.add(operations_group)

        today = timezone.now().date()
        shifts = ['A', 'B', 'C', 'G']
        
        # Create operations data
        for shift in shifts:
            # Area 1 Operations
            Area1Operation.objects.create(
                date=today,
                shift=shift,
                feeding_quantity=random.randint(800, 2000),
                receiving_quantity=random.randint(600, 1500),
                reclaiming_quantity=random.randint(500, 1200),
                created_by=test_user
            )
            
            # Area 2&3 Operations
            Area23Operation.objects.create(
                date=today,
                shift=shift,
                feeding_quantity=random.randint(1000, 2500),
                receiving_quantity=random.randint(800, 2000),
                crushing_quantity=random.randint(700, 1800),
                base_mix_quantity=random.randint(600, 1500),
                created_by=test_user
            )
        
        # Create delays
        delay_types = ['MECHANICAL', 'ELECTRICAL', 'OPERATIONAL']
        for delay_type in delay_types:
            Delay.objects.create(
                date=today,
                shift=random.choice(shifts),
                delay_type=delay_type,
                area=random.choice(['AREA_1', 'AREA_2', 'AREA_3']),
                equipment=random.choice(['CONVEYOR', 'STACKER', 'RECLAIMER', 'CRUSHER', 'SCREEN', 'WAGON_TIPPLER', 'SIDE_ARM_CHARGER', 'OTHER']),
                equipment_id=f"EQ-{random.randint(1000, 9999)}",
                start_time=timezone.now().time(),
                end_time=(timezone.now() + timedelta(hours=random.uniform(0.5, 4.0))).time(),
                duration_hours=random.uniform(0.5, 4.0),
                delay_reason=f"Test {delay_type.lower()} delay reason",
                action_taken="Test action taken to resolve the delay",
                is_resolved=random.choice([True, False]),
                created_by=test_user
            )
        
        # Create rakes
        for _ in range(5):
            Rake.objects.create(
                date=today,
                shift=random.choice(shifts),
                rake_id=f"RK-{random.randint(10000, 99999)}",
                material_type=random.choice(['COAL', 'IRON_ORE', 'LIMESTONE', 'DOLOMITE', 'COKE', 'OTHER']),
                supplier=f"Supplier-{random.randint(1, 5)}",
                total_wagons=random.randint(30, 60),
                wagon_capacity=random.uniform(50, 70),
                total_quantity=random.uniform(2000, 4000),
                arrival_time=timezone.now() - timedelta(hours=random.uniform(1, 5)),
                unloading_start_time=timezone.now() - timedelta(hours=random.uniform(0.5, 3)),
                unloading_end_time=timezone.now() if random.choice([True, False]) else None,
                status=random.choice(['RECEIVED', 'UNLOADING', 'COMPLETED', 'DISPATCHED']),
                unloading_equipment=random.choice(['Wagon Tippler', 'Side Arm Charger', 'Manual']),
                demurrage_hours=random.uniform(0, 5),
                created_by=test_user
            )
        
        # Create maintenance activities
        maintenance_types = ['MECHANICAL', 'ELECTRICAL']
        for _ in range(3):
            MaintenanceActivity.objects.create(
                date=today,
                shift=random.choice(shifts),
                maintenance_type=random.choice(maintenance_types),
                maintenance_category=random.choice(['PREVENTIVE', 'BREAKDOWN', 'CORRECTIVE', 'PREDICTIVE', 'ROUTINE']),
                area=random.choice(['AREA_1', 'AREA_2', 'AREA_3']),
                equipment=random.choice(['CONVEYOR', 'STACKER', 'RECLAIMER', 'CRUSHER', 'SCREEN', 'WAGON_TIPPLER', 'SIDE_ARM_CHARGER', 'OTHER']),
                equipment_id=f"EQ-{random.randint(1000, 9999)}",
                activity_description="Routine maintenance check",
                spares_used="Bearings, Belts, Lubricants",
                start_time=timezone.now().time(),
                end_time=(timezone.now() + timedelta(hours=random.uniform(1, 4))).time(),
                duration_hours=random.uniform(1, 4),
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
                is_completed=random.choice([True, False]),
                created_by=test_user
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 