# -*- coding: utf-8 -*-
"""
Modified on Tue Feb 25 18:30:03 2025

@author: Franz Hentze
"""

# Function to calculate Cation Exchange Capacity (CEC)
def calculate_cec(ca_cmol, mg_cmol, k_cmol, na_cmol, al_cmol):
    return ca_cmol + mg_cmol + k_cmol + na_cmol + al_cmol

# Given values (cmol+/kg)
given_values = {
    "ca_cmol": 12,
    "mg_cmol": 2.34,
    "k_cmol": 0.8,
    "na_cmol": 0,
    "al_cmol": 0.08,
    "ph_value": 6.44,
}

# Fixed matrix for pH, Hydrogen, and Other Bases
ph_matrix = {
    3.00: (75.0, 11.4), 3.10: (74.0, 11.2), 3.20: (73.0, 11.0), 3.30: (72.0, 10.8),
    3.40: (71.0, 10.6), 3.50: (70.0, 10.4), 3.60: (69.0, 10.2), 3.70: (68.0, 10.0),
    3.80: (67.0, 9.8), 3.90: (66.0, 9.6), 4.00: (65.0, 9.4), 4.10: (63.0, 9.2),
    4.20: (61.0, 9.0), 4.30: (59.0, 8.8), 4.40: (57.0, 8.6), 4.50: (55.0, 8.4),
    4.60: (53.0, 8.2), 4.70: (51.0, 8.0), 4.80: (49.0, 7.8), 4.90: (47.0, 7.6),
    5.00: (45.0, 7.4), 5.10: (42.0, 7.2), 5.20: (39.0, 7.0), 5.30: (36.0, 6.8),
    5.40: (33.0, 6.6), 5.50: (30.0, 6.4), 5.60: (27.0, 6.2), 5.70: (24.0, 6.0),
    5.80: (21.0, 5.8), 5.90: (18.0, 5.6), 6.00: (15.0, 5.4), 6.10: (13.5, 5.3),
    6.20: (12.0, 5.2), 6.30: (10.5, 5.1), 6.40: (9.0, 5.0), 6.50: (7.5, 4.9),
    6.60: (6.0, 4.8), 6.70: (4.5, 4.7), 6.80: (3.0, 4.6), 6.90: (1.5, 4.5),
    7.00: (0.0, 4.4), 7.10: (0.0, 4.3), 7.20: (0.0, 4.2), 7.30: (0.0, 4.1),
    7.40: (0.0, 4.0), 7.50: (0.0, 3.9), 7.60: (0.0, 3.8), 7.70: (0.0, 3.7),
    7.80: (0.0, 3.6), 7.90: (0.0, 3.5), 8.00: (0.0, 3.4), 8.10: (0.0, 3.3),
    8.20: (0.0, 3.2), 8.30: (0.0, 3.1), 8.40: (0.0, 3.0), 8.50: (0.0, 2.9),
}

# Ensure given pH exists in the matrix, otherwise find closest match
closest_pH = min(ph_matrix.keys(), key=lambda x: abs(x - given_values["ph_value"]))
hydrogen_percentage, other_bases_percentage = ph_matrix[closest_pH]

# Calculate CEC
cec = calculate_cec(
    given_values["ca_cmol"], given_values["mg_cmol"], given_values["k_cmol"],
    given_values["na_cmol"], given_values["al_cmol"]
)

# Assign multiplier based on pH ranges
ph = given_values["ph_value"]

# Assign multiplier based on refined pH ranges
if ph < 4.5:
    multiplier = 2.1
elif ph < 5.0:
    multiplier = 2
elif ph < 5.3:
    multiplier = 1.9
elif ph < 5.5:
    multiplier = 1.8
elif ph < 5.7:
    multiplier = 1.6
elif ph < 5.9:
    multiplier = 1.4
elif ph < 6.1:
    multiplier = 1.2
elif ph < 6.3:
    multiplier = 0.9
elif ph < 6.5:
    multiplier = 0.7
elif ph < 6.7:
    multiplier = 0.3
elif ph < 7.0:
    multiplier = 0.1
else:
    multiplier = 0.05


# Calculate Hydrogen and Other Bases (cmol+/kg)
hydrogen_cmol = ((hydrogen_percentage / 100) * cec) * multiplier
other_bases_cmol = ((other_bases_percentage / 100) * cec) * multiplier

# Calculate Total Exchangeable Cations (TEC)
tec = cec + hydrogen_cmol + other_bases_cmol

# Calculate Base Saturation Percentages
base_saturation = {
    "Ca": (given_values["ca_cmol"] / tec) * 100,
    "Mg": (given_values["mg_cmol"] / tec) * 100,
    "K": (given_values["k_cmol"] / tec) * 100,
    "Na": (given_values["na_cmol"] / tec) * 100,
    "Al": (given_values["al_cmol"] / tec) * 100,
    "H": hydrogen_percentage,
}

# Calculate Other Bases %, ensuring it does not go negative
base_saturation["Other_Bases"] = max(0, 100 - sum([
    base_saturation["Ca"], base_saturation["Mg"], base_saturation["K"],
    base_saturation["Na"], base_saturation["Al"], base_saturation["H"]
]))

# Print results
print(f"Cation Exchange Capacity (CEC): {cec:.2f} cmol+/kg")
print(f"Total Exchangeable Cations (TEC): {tec:.2f} cmol+/kg")
for element, percentage in base_saturation.items():
    print(f"{element} Base Saturation: {percentage:.2f}%")