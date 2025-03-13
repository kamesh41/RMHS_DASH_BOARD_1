# Equipment presets - to be used in views for populating select fields
EQUIPMENT_PRESETS = {
    'reclaiming': {
        'stacker_reclaimer_1': {
            'name': 'Stacker Reclaimer 1',
            'capacity': '1000 MT/h'
        },
        'stacker_reclaimer_2': {
            'name': 'Stacker Reclaimer 2',
            'capacity': '1000 MT/h'
        },
        'stacker_reclaimer_3': {
            'name': 'Stacker Reclaimer 3',
            'capacity': '1200 MT/h'
        },
        'reclaimer_1': {
            'name': 'Reclaimer 1',
            'capacity': '800 MT/h'
        },
        'reclaimer_2': {
            'name': 'Reclaimer 2',
            'capacity': '800 MT/h'
        }
    },
    'feeding': {
        'conveyor_a1': {
            'name': 'Conveyor A1',
            'capacity': '1000 MT/h'
        },
        'conveyor_a2': {
            'name': 'Conveyor A2',
            'capacity': '1000 MT/h'
        },
        'conveyor_a3': {
            'name': 'Conveyor A3',
            'capacity': '1200 MT/h'
        },
        'conveyor_b1': {
            'name': 'Conveyor B1',
            'capacity': '800 MT/h'
        },
        'conveyor_b2': {
            'name': 'Conveyor B2',
            'capacity': '800 MT/h'
        }
    },
    'receiving': {
        'unloader_1': {
            'name': 'Unloader 1',
            'capacity': '1000 MT/h'
        },
        'unloader_2': {
            'name': 'Unloader 2',
            'capacity': '1000 MT/h'
        },
        'wagon_tippler_1': {
            'name': 'Wagon Tippler 1',
            'capacity': '1200 MT/h'
        },
        'wagon_tippler_2': {
            'name': 'Wagon Tippler 2',
            'capacity': '1200 MT/h'
        }
    },
    'crushing': {
        'crusher_1': {
            'name': 'Crusher 1',
            'capacity': '300 MT/h'
        },
        'crusher_2': {
            'name': 'Crusher 2',
            'capacity': '300 MT/h'
        },
        'crusher_3': {
            'name': 'Crusher 3',
            'capacity': '400 MT/h'
        }
    },
    'base_mix': {
        'mixer_1': {
            'name': 'Mixer 1',
            'capacity': '200 MT/h'
        },
        'mixer_2': {
            'name': 'Mixer 2',
            'capacity': '200 MT/h'
        },
        'mixer_3': {
            'name': 'Mixer 3',
            'capacity': '250 MT/h'
        }
    }
}

# Equipment Choices - to be used in forms
RECLAIMING_EQUIPMENT_CHOICES = [
    ('', '---------'),
    ('stacker_reclaimer_1', 'Stacker Reclaimer 1'),
    ('stacker_reclaimer_2', 'Stacker Reclaimer 2'),
    ('stacker_reclaimer_3', 'Stacker Reclaimer 3'),
    ('reclaimer_1', 'Reclaimer 1'),
    ('reclaimer_2', 'Reclaimer 2'),
    ('other', 'Other (specify)'),
]

FEEDING_EQUIPMENT_CHOICES = [
    ('', '---------'),
    ('conveyor_a1', 'Conveyor A1'),
    ('conveyor_a2', 'Conveyor A2'),
    ('conveyor_a3', 'Conveyor A3'),
    ('conveyor_b1', 'Conveyor B1'),
    ('conveyor_b2', 'Conveyor B2'),
    ('other', 'Other (specify)'),
]

RECEIVING_EQUIPMENT_CHOICES = [
    ('', '---------'),
    ('unloader_1', 'Unloader 1'),
    ('unloader_2', 'Unloader 2'),
    ('wagon_tippler_1', 'Wagon Tippler 1'),
    ('wagon_tippler_2', 'Wagon Tippler 2'),
    ('other', 'Other (specify)'),
]

CRUSHING_EQUIPMENT_CHOICES = [
    ('', '---------'),
    ('crusher_1', 'Crusher 1'),
    ('crusher_2', 'Crusher 2'),
    ('crusher_3', 'Crusher 3'),
    ('other', 'Other (specify)'),
]

BASE_MIX_EQUIPMENT_CHOICES = [
    ('', '---------'),
    ('mixer_1', 'Mixer 1'),
    ('mixer_2', 'Mixer 2'),
    ('mixer_3', 'Mixer 3'),
    ('other', 'Other (specify)'),
]

DESTINATION_CHOICES = [
    ('', '---------'),
    ('stockpile', 'Stockpile'),
    ('sinter_plant', 'Sinter Plant'),
    ('blast_furnace', 'Blast Furnace'),
    ('coke_oven', 'Coke Oven'),
    ('crushing_unit', 'Crushing Unit'),
    ('base_mix_unit', 'Base Mix Unit'),
    ('other', 'Other (specify)'),
]

SOURCE_CHOICES = [
    ('', '---------'),
    ('yard', 'RMHS Yard'),
    ('rail', 'Rail'),
    ('truck', 'Truck'),
    ('conveyor', 'Conveyor'),
    ('port', 'Port'),
    ('other', 'Other (specify)'),
] 