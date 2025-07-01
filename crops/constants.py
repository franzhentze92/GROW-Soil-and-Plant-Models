# Define fertiliser matrix with nutrient composition and costs
fertiliser_matrix = {
    'Amino-Max': {'N': 1, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Phos-Force': {'N': 0, 'P': 1, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'K-Rich': {'N': 0, 'P': 0, 'K': 1, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Cal-Tech': {'N': 0, 'P': 0, 'K': 0, 'Ca': 1, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Mag-Life': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 1, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Iron Essentials': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 1, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Copper Essentials': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 1, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Manganese Essentials': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 1, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Zinc Essentials': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 1, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Boron Essentials': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 1, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Triple Ten': {'N': 1, 'P': 1, 'K': 1, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Trio': {'N': 0, 'P': 0, 'K': 0, 'Ca': 1, 'Mg': 1, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 1, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Multi-Min': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 1, 'Cu': 1, 'Mn': 1, 'Zn': 1, 'B': 1, 'Si': 0, 'Mo': 0, 'Co': 0},
    'Shuttle Seven': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 1, 'Cu': 1, 'Mn': 1, 'Zn': 1, 'B': 1, 'Si': 0, 'Mo': 1, 'Co': 1},
    'Potassium Silicate': {'N': 0, 'P': 0, 'K': 1, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 1, 'Mo': 0, 'Co': 0},
    'Moly Shuttle': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 1, 'Co': 0, },
    'Cobalt Shuttle': {'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co': 1},
    'CalMag': {'N': 0, 'P': 0, 'K': 0, 'Ca': 1, 'Mg': 1, 'Fe': 0, 'Cu': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Si': 0, 'Mo': 0, 'Co':0}
}

# Define control switches and percentage thresholds
REQUIRE_AT_LEAST_X_PERCENT_DEFICIENT = True  # Recommend if at least X% of nutrients are deficient
REQUIRE_EXACTLY_Y_PERCENT_DEFICIENT = False  # Recommend only if exactly Y% of nutrients are deficient
X_PERCENT_THRESHOLD = 10  # Set threshold for "at least" rule
Y_PERCENT_THRESHOLD = 100  # Set threshold for "exactly" rule