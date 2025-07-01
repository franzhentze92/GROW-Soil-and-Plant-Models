# -*- coding: utf-8 -*-
"""
Modified on Sat May  3 2025

@author: Franz Hentze
"""

# Alot of changes were made to this code version
# refer to the helpers.py version for the latest

import pprint

def calculate_cec(ca_cmol, mg_cmol, k_cmol, na_cmol, al_cmol):
    return ca_cmol + mg_cmol + k_cmol + na_cmol + al_cmol

def calculate_obresult(hydrogen_percent, other_bases_percent, cec_value, step=0.0001):
    obresult = 0.0
    if other_bases_percent > 0:
        while True:
            F10 = round((obresult * hydrogen_percent) / other_bases_percent, 9)
            tec_value = round(cec_value + obresult + F10, 9)
            ratio = round((obresult * 100) / tec_value, 9)
            if ratio > other_bases_percent:
                break
            obresult += step
        obresult = round(obresult - step, 9)
        F10 = round((obresult * hydrogen_percent) / other_bases_percent, 9)
    else:
        while True:
            tec_value = round(cec_value + obresult, 9)
            ratio = round((obresult * 100) / tec_value, 9)
            if ratio > hydrogen_percent:
                break
            obresult += step
        obresult = round(obresult - step, 9)
        F10 = 0.0

    F10_adjusted = round(F10 * 0.9, 9)
    tec_final = round(cec_value + F10_adjusted, 9)
    return obresult, F10_adjusted, tec_final

def round_ph_custom(ph):
    int_part = int(ph * 10)
    decimal = (ph * 10) - int_part
    if decimal >= 0.5:
        return round((int_part + 1) / 10, 2)
    else:
        return round(int_part / 10, 2)


tec_matrix = [
    {"min": 1.0, "max": 3.0, "ratio": 3.0, "Ca": 60.0, "Mg": 20.0, "K": (5.0, 7.0)},
    {"min": 3.0, "max": 5.0, "ratio": 3.4, "Ca": 62.0, "Mg": 18.0, "K": (5.0, 7.0)},
    {"min": 5.0, "max": 7.0, "ratio": 4.0, "Ca": 64.0, "Mg": 16.0, "K": (4.0, 5.0)},
    {"min": 7.0, "max": 9.0, "ratio": 4.3, "Ca": 65.0, "Mg": 15.0, "K": (3.5, 5.0)},
    {"min": 9.0, "max": 11.0, "ratio": 5.2, "Ca": 67.0, "Mg": 13.0, "K": (3.0, 5.0)},
    {"min": 11.0, "max": 30.0, "ratio": 5.7, "Ca": 68.0, "Mg": 12.0, "K": (3.0, 5.0)},
    {"min": 30.0, "max": 100000.0, "ratio": 7.0, "Ca": 70.0, "Mg": 10.0, "K": (2.0, 5.0)},
]

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

# ppm_input = {
#     "ca_ppm": 3780,
#     "mg_ppm": 189,
#     "k_ppm": 697,
#     "na_ppm": 56,
#     "al_ppm": 7,
#     "ph_value": 7.40,
# }

ppm_input = {
    "ca_ppm": 237.0,
    "mg_ppm": 36.4,
    "k_ppm": 67.1,
    "na_ppm": 0,
    "al_ppm": 1.0,
    "ph_value": 6,
}


given_values = {
    "ca_cmol": ppm_input["ca_ppm"] / 200,
    "mg_cmol": ppm_input["mg_ppm"] / 120,
    "k_cmol": ppm_input["k_ppm"] / 390,
    "na_cmol": ppm_input["na_ppm"] / 230,
    "al_cmol": ppm_input["al_ppm"] / 90,
    "ph_value": ppm_input["ph_value"],
}

closest_pH = min(ph_matrix.keys(), key=lambda x: abs(x - given_values["ph_value"]))
hydrogen_percentage, other_bases_percentage = ph_matrix[closest_pH]

print("Closest pH value: ", closest_pH)
print("Hydrogen percentage: ", hydrogen_percentage)
print("Other bases percentage: ", other_bases_percentage)

cec = calculate_cec(
    given_values["ca_cmol"], given_values["mg_cmol"],
    given_values["k_cmol"], given_values["na_cmol"],
    given_values["al_cmol"]
)
print(f"Calculated CEC: {cec}")

hydrogen_cmol, other_bases_cmol, tec = calculate_obresult(
    hydrogen_percentage, other_bases_percentage, cec
)

print("TEC: ", tec)

base_saturation = {
    "Ca": (given_values["ca_cmol"] / tec) * 100,
    "Mg": (given_values["mg_cmol"] / tec) * 100,
    "K": (given_values["k_cmol"] / tec) * 100,
    "Na": (given_values["na_cmol"] / tec) * 100,
    "Al": (given_values["al_cmol"] / tec) * 100,
    "H": hydrogen_percentage,
}
base_saturation["Other_Bases"] = max(0, 100 - sum(base_saturation.values()))

real_ca_mg_ratio = (
    given_values["ca_cmol"] / given_values["mg_cmol"]
    if given_values["mg_cmol"] != 0 else None
)

ideal_ca_mg_ratio = None
ideal_ranges = {
    "Al": (0, 0.5),
    "H": (0, 10),
    "Other_Bases": (0, 5),
}
ideal_values_to_show = {}
ideal_ppm_ranges = {}

for entry in tec_matrix:
    if entry["min"] <= tec < entry["max"]:
        ideal_ca_mg_ratio = entry["ratio"]
        if tec < 4:
            ideal_ranges["Ca"] = (46.5, 77.5)
            ideal_ranges["Mg"] = (13.5, 22.5)
            ideal_ranges["K"] = (5.0, 7.0)
            ideal_ranges["Na"] = (0.5, 1.5)
            # ideal_ranges["Al"] = (0.0, 2.0) // client requested to update this later
            ideal_values_to_show["Ca"] = 62.0
            ideal_values_to_show["Mg"] = 18.0

            ideal_ppm_ranges = {
                "Ca": (372, 620),
                "Mg": (64.5, 107.5),
                "K": (78, 109),
                "Na": (5, 14),
                "Al": (0, 2),
            }
        else:
            ideal_ranges["Ca"] = (entry["Ca"] * 0.7515, entry["Ca"] * 1.25)
            ideal_ranges["Mg"] = (entry["Mg"] * 0.7515, entry["Mg"] * 1.25)
            ideal_ranges["K"] = entry["K"]
            ca_ppm_range = (
                round((entry["Ca"] * 0.7515 / 100) * tec * 200),
                round((entry["Ca"] * 1.25 / 100) * tec * 200),
            )
            mg_ppm_range = (
                round((entry["Mg"] * 0.7515 / 100) * tec * 120),
                round((entry["Mg"] * 1.25 / 100) * tec * 120),
            )
            ideal_ppm_ranges = {
                "Ca": ca_ppm_range,
                "Mg": mg_ppm_range,
                "K": (
                    round(entry["K"][0] / 100 * tec * 390),
                    round(entry["K"][1] / 100 * tec * 390),
                ),
                "Na": (
                    round(0.5 / 100 * tec * 230),
                    round(1.5 / 100 * tec * 230),
                ),
                "Al": (
                    0,
                    round(0.5 / 100 * tec * 90),
                ),
            }
            ideal_values_to_show["Ca"] = (ideal_ranges["Ca"][0] + ideal_ranges["Ca"][1]) / 2
            ideal_values_to_show["Mg"] = (ideal_ranges["Mg"][0] + ideal_ranges["Mg"][1]) / 2

        ideal_ranges["Na"] = (0.5, 1.5)
        ideal_values_to_show["K"] = entry["K"]
        ideal_values_to_show["Na"] = 1.0
        break

# Output
print(f"Rounded pH used for calculation: {closest_pH:.2f}")
print(f"Cation Exchange Capacity (CEC): {cec:.2f} cmol+/kg")
print(f"Total Exchangeable Cations (TEC): {tec:.2f} cmol+/kg\n")

for element, percentage in base_saturation.items():
    print(f"{element} Base Saturation: {percentage:.2f}%")
    if element in ideal_ranges or element in ["Ca", "Mg"]:
        min_val, max_val = ideal_ranges.get(element, (0.0, 0.0))
        print(f" -> Ideal Range: {min_val:.2f}% to {max_val:.2f}%")
        if element in ["Ca", "Mg"]:
            ideal_val = ideal_values_to_show.get(element)
            if ideal_val is not None:
                print(f" -> Ideal Value to Show in Report: {ideal_val:.0f}%")
        else:
                print(f" -> Ideal Value to Show in Report: {min_val:.2f}% to {max_val:.2f}%")

print()
if real_ca_mg_ratio:
    print(f"Real Ca/Mg Ratio: {real_ca_mg_ratio:.2f}")
else:
    print("Real Ca/Mg Ratio: Not defined (magnesium or calcium is zero)")

if ideal_ca_mg_ratio:
    print(f"Ideal Ca/Mg Ratio: {ideal_ca_mg_ratio}:1")
else:
    print("Ideal Ca/Mg Ratio: Not found for this TEC")

print("\nIdeal PPM Ranges:")
for element, (min_ppm, max_ppm) in ideal_ppm_ranges.items():
    if element in ["Ca", "Mg"]:
        midpoint = (min_ppm + max_ppm) / 2
        print(f"{element}: {int(midpoint)} ppm (midpoint of {min_ppm}–{max_ppm})")
    else:
        print(f"{element}: {min_ppm}–{max_ppm} ppm")


print("separating for debugging")
pprint.pp(ideal_ranges)
pprint.pp(ideal_values_to_show)
pprint.pp(ideal_ppm_ranges)
pprint.pp(base_saturation)