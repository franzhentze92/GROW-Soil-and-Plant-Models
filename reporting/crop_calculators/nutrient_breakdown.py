# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 15:44:41 2025

@author: Franz Hentze
"""

# Hardcoded nutrient breakdown as a Python dictionary
PRODUCT_DATA = {
    "K-Rich™": {"K": 33.29},
    "Cal-Tech™": {"N": 11.71, "B": 0.43, "Ca": 13.36},
    "Calcium Fulvate™": {"N": 6.78, "S": 0.54, "B": 0.0207, "Ca": 8.93, "Cu": 0.0785, "Zn": 0.0807, "Fe": 0.17, "K": 1.32, "Mn": 0.21, "Mo": 0.0102},
    "Citrus-Tech Triple Ten™": {"N": 10.48, "S": 0.22, "B": 0.0347, "Ca": 0.0558, "Cu": 0.0197, "P": 10.23, "Zn": 0.0743, "Fe": 0.1459, "K": 10.69, "Mn": 0.0607, "Mo": 0.0039, "Se": 0.0198},
    "Cloak Spray Oil™": {},
    "Nutri-Carb-N™": {"N": 15.18, "K": 1.1},
    "Phos-Force™": {"N": 4.2, "Ca": 4.3, "P": 14.3, "Fe": 3.5},
    "Photo-Finish™": {"K": 10.6, "Si": 10.38},
    "Potassium Silicate™": {"K": 15.3, "Si": 17.3},
    "Seed-Start™": {},
    "Trio (CMB)™": {"N": 13.73, "B": 0.26, "Mg": 2.38, "Ca": 15.3, "Zn": 0.006, "Fe": 0.1},
    "Triple Ten™": {"N": 10.48, "S": 0.22, "B": 0.0347, "Ca": 0.0558, "Cu": 0.0197, "P": 10.23, "Zn": 0.0743, "Fe": 0.1459, "K": 10.69, "Mn": 0.0607, "Mo": 0.0039, "Se": 0.0198},
    "Potassium Silicate™": {"K": 15.3, "Si": 17.3},
    "Seed-Start™": {},
    "Trio (CMB)™": {"N": 13.73, "B": 0.26, "Mg": 2.38, "Ca": 15.3, "Zn": 0.006, "Fe": 0.1},
    "Triple Ten™": {"N": 10.48, "S": 0.22, "B": 0.0347, "Ca": 0.0558, "Cu": 0.0197, "P": 10.23, "Zn": 0.0743, "Fe": 0.1459, "K": 10.69, "Mn": 0.0607, "Mo": 0.0039, "Se": 0.0198},
    "Tsunami™ Super Spreader": {},
    "Activated Char Condensate (ACC)™": {},
    "Aloe-Tech™": {},
    "Amino-Max™": {"N": 5.78, "Amino Acids": 40},
    "Brix-Fix™": {},
    "Nutri-Kelp™": {},
    "Nutri-Sea Liquid Fish™": {},
    "Nutri-Stim Saponins™": {},
    "Nutri-Stim Triacontanol™": {},
    "Nutri-Tech Black Gold®": {},
    "Root & Shoot™": {},
    "SeaChange KFF™": {},
    "SeaChange Liquid Kelp™": {},
    "Tri-Kelp™": {},
    "Nutri-Key Boron Shuttle™": {"N": 0.29, "S": 0.53, "B": 3.61, "Mg": 0.0938, "Cu": 0.049, "Zn": 0.19, "Fe": 0.31, "K": 0.51, "Mn": 0.15, "Mo": 0.0098, "Carbon": 3.38},
    "Nutri-Key Calcium Shuttle™": {"N": 7.25, "S": 0.26, "B": 0.0433, "Mg": 0.0363, "Ca": 9.81, "Cu": 0.0245, "Zn": 0.093, "Fe": 0.15, "K": 0.23, "Mn": 0.0757, "Mo": 0.0049, "Si": 0.0217, "Carbon": 5.27},
    "Nutri-Key Cobalt Shuttle™": {"Co": 3.1, "Zn": 2.8},
    "Nutri-Key Copper Shuttle™": {"N": 0.52, "S": 4.29, "B": 0.0866, "Mg": 0.0675, "Cu": 7.64, "Zn": 0.19, "Fe": 0.31, "K": 0.27, "Mn": 0.15, "Mo": 0.0098, "Carbon": 4.62},
    "Nutri-Key Hydro-Shuttle™": {"N": 2.14, "Carbon": 21.15},
    "Nutri-Key Iron Shuttle™": {"N": 0.52, "S": 4.41, "B": 0.0866, "Mg": 0.0678, "Cu": 0.049, "Zn": 0.19, "Fe": 7.21, "K": 0.34, "Mn": 0.15, "Mo": 0.0098, "Carbon": 4.38},
    "Nutri-Key Magnesium Shuttle™": {"N": 0.45, "S": 6.24, "B": 0.0866, "Mg": 4.44, "Cu": 0.049, "Zn": 0.19, "Fe": 0.31, "K": 0.31, "Mn": 0.15, "Mo": 0.0098, "Carbon": 3.9},
    "Nutri-Key Manganese Shuttle™": {"N": 0.53, "S": 8.15, "B": 0.0866, "Mg": 0.0675, "Cu": 0.049, "Zn": 0.19, "Fe": 0.31, "K": 0.27, "Mn": 13.19, "Mo": 0.0098, "Carbon": 4.7},
    "Nutri-Key Moly Shuttle™": {"N": 0.18, "Mo": 4.76, "Carbon": 1.6},
    "Nutri-Key Shuttle Seven™": {"N": 0.43, "S": 4.72, "B": 0.87, "Mg": 0.67, "Co": 0.000034, "Cu": 0.49, "Zn": 1.86, "Fe": 3.06, "K": 2.63, "Mn": 1.51, "Mo": 0.000975, "Se": 0.43, "Carbon": 3.04},
    "Nutri-Key Zinc Shuttle™": {"N": 0.73, "S": 4.35, "B": 0.0866, "Mg": 0.0675, "Cu": 0.049, "Zn": 8.17, "Fe": 0.31, "K": 0.27, "Mn": 0.15, "Mo": 0.0098, "Carbon": 6.54},
    "Boron Essentials™": {"N": 0.05, "B": 3.09, "Zn": 0.04},
    "Copper Essentials™": {"N": 0.12, "S": 2.55, "Mg": 0.0352, "Ca": 0.0247, "Cu": 4.9, "K": 0.14},
    "Iron Essentials™": {"N": 0.12, "S": 3.49, "Mg": 0.0351, "Ca": 0.0247, "Fe": 6, "K": 0.14},
    "Manganese Essentials™": {"N": 0.12, "S": 6.52, "Mg": 0.0352, "Ca": 0.0247, "Mn": 0.13, "Si": 10.96},
    "Multi-Boost™": {"N": 2.29, "S": 6.2, "B": 0.033, "Mg": 0.64, "Ca": 5.96, "Cu": 0.0245, "P": 0.29, "Zn": 0.0536, "Fe": 0.0708, "K": 0.66, "Mn": 0.0483, "Mo": 0.013},
    "Multi-Min™": {"N": 4.24, "S": 4.12, "B": 0.2, "Mg": 1.49, "Ca": 0.0186, "Cu": 0.78, "P": 0.17, "Zn": 0.81, "Fe": 1.44, "K": 2.45, "Mn": 2.05, "Mo": 0.1},
    "Multi-Plex™": {"N": 10.22, "S": 0.23, "B": 0.0347, "Cu": 0.0198, "P": 10.09, "Zn": 0.0743, "Fe": 0.14, "K": 10.04, "Mn": 0.0607, "Mo": 0.0039},
    "Zinc Essentials™": {"N": 0.12, "S": 3.95, "Mg": 0.0351, "Ca": 0.0247, "Zn": 7.95, "Fe": 0.14},
    "CalMag-Life Organic™": {"Mg": 9.68, "Ca": 20.26},
    "Dia-Life Organic™": {"B": 0.68, "Mg": 0.0277, "Ca": 0.16, "Fe": 0.32, "Si": 12.51},
    "Gyp-Life Organic™": {"S": 15.31, "Ca": 19.55},
    "Lime-Life Organic™": {"Mg": 1.05, "Ca": 39.37},
    "Mag-Life Organic™": {"Mg": 21.33},
    "Phos-Life Organic™": {"Mg": 0.34, "Ca": 24.56, "Cu": 0.0162, "P": 10.71, "Zn": 0.14, "Fe": 0.86, "K": 0.15, "Mn": 1.66, "Si": 10.73},
    "Sili-Cal (B)™": {"S": 0.13, "B": 0.51, "Mg": 0.64, "Ca": 21.59, "Fe": 0.0861, "K": 0.23, "Si": 3.34},
    "Life Force® Carbon™": {},
    "Life Force® Gold Pellets™": {},
    "NTS Soft Rock™": {},
    "Nutri-Gyp™ Natural Gypsum": {},
    "Nutri-Phos Super Active™": {},
    "NTS Fast Fulvic™": {},
    "NTS Fulvic Acid Powder™": {},
    "NTS FulvX™ Powder": {},
    "NTS Liquid Humus™": {},
    "NTS Soluble Humate Granules™": {},
    "NTS Stabilised Boron Granules™": {},
    "NTS Super Soluble Humates™": {},
    "Nutri-Life B.Sub™": {},
    "Nutri-Life BAM™": {},
    "Nutri-Life Bio-N™": {},
    "Nutri-Life Bio-Plex™": {},
    "Nutri-Life Bio-P™": {},
    "Nutri-Life Micro-Force™": {},
    "Nutri-Life Myco-Force™": {},
    "Nutri-Life Platform®": {},
    "Nutri-Life Root-Guard™": {},
    "Nutri-Life Tricho-Shield™": {},
    "Urea (Source locally)": {"N": 46},
    "Sodium Molybdate (Source locally)": {},
    "Soluble Boron (Source locally)": {"B": 20},
    "Calcium Nitrate (Source locally)": {"N": 15.5, "Ca": 19},
    "MAP (Source locally)": {"N": 10, "P": 22},
    "DAP (Source locally)": {"N": 18, "P": 20},
    "Potassium Sulfate (Source locally)": {"S": 17, "K": 50},
    "Magnesium Sulfate (Source locally)": {"S": 13, "Mg": 9.8},
    "Ammonium Sulfate (Source locally)": {"N": 21, "S": 24},
    "Iron Sulfate (Source locally)": {"S": 11.4, "Fe": 19.7},
    "Manganese Sulfate (Source locally)": {"S": 18, "Mn": 31},
    "Copper Sulfate (Source locally)": {"S": 12.8, "Cu": 25},
    "Zinc Sulfate (Source locally)": {"S": 17.9, "Zn": 23},
    "MKP (Source locally)": {"P": 22.7, "K": 28.7},
    "Chicken Manure (Source locally)": {"N": 2, "S": 0.5, "B": 0.05, "Mg": 0.6, "Ca": 8, "Cu": 0.2, "P": 1.8, "Zn": 0.35, "Fe": 0.7, "K": 1.2, "Mn": 0.5, "Carbon": 30},
    "Worm Juice (Source locally)": {"N": 1.5, "S": 0.5, "Mg": 0.2, "Ca": 1, "Zn": 0.5, "Fe": 0.3},
    "Elemental Sulfur (Source locally)": {"S": 90},
    "Dolomite (Source locally)": {"Mg": 22, "Ca": 30},
    "Lime (Source locally)": {"Ca": 38},
    "Gypsum (Source locally)": {"S": 17, "Ca": 22},
    "Magnesite (Source locally)": {"Mg": 47.8},
    "Potassium Nitrate (Source locally)": {"N": 13, "K": 44},
    "Borax (Source locally)": {"B": 11.3},
    "Magnesium Oxide (Source locally)": {"Mg": 60},
    "Tri-Shuttle CBZ™": {"Zn": 3.57, "Cu": 2.09, "B": 0.32, "N": 0.47, "K": 0.22, "C": 4.19, "S": 3.06, "Fe": 0.23, "Mn": 0.11, "Mg": 0.051, "Mo": 0.0074},
    "Tri-Shuttle ZIM™": {"Zn": 4.18, "Mn": 2.95, "Fe": 2.38, "N": 0.63, "K": 0.29, "C": 5.53, "S": 5.24, "B": 0.0866, "Mg": 0.0676, "Cu": 0.049, "Mo": 0.0098},
}

# Default soil weight for ppm calculation
SOIL_WEIGHT = 2_240_000

def get_user_input(prompt_message, options):
    """Provide a simple input mechanism to select from options."""
    print(f"{prompt_message}")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_nutrient_breakdown(product_name, amount_kg):
    """Calculate kg/ha and ppm for nutrients based on hardcoded data."""
    if product_name not in PRODUCT_DATA:
        raise ValueError(f"No data found for product: {product_name}")

    nutrient_data = PRODUCT_DATA[product_name]
    results = []
    for nutrient, percentage in nutrient_data.items():
        kg_per_ha = (amount_kg * percentage) / 100
        ppm = (kg_per_ha * 1_000_000) / SOIL_WEIGHT
        results.append({"Nutrient": nutrient, "kg/ha": kg_per_ha, "ppm": ppm})
    return results

def calculate_combined_nutrient_breakdown(products_with_amounts):
    """Calculate combined nutrient breakdown for multiple products."""
    combined_results = {}
    for product, amount in products_with_amounts.items():
        if product not in PRODUCT_DATA:
            raise ValueError(f"No data found for product: {product}")
            # continue

        nutrient_data = PRODUCT_DATA[product]
        for nutrient, percentage in nutrient_data.items():
            kg_per_ha = (amount * percentage) / 100
            if nutrient in combined_results:
                combined_results[nutrient] += kg_per_ha
            else:
                combined_results[nutrient] = kg_per_ha

    final_results = []
    for nutrient, total_kg_per_ha in combined_results.items():
        ppm = (total_kg_per_ha * 1_000_000) / SOIL_WEIGHT
        final_results.append({"Nutrient": nutrient, "kg/ha": total_kg_per_ha, "ppm": ppm})
    return final_results

# def main():
#     """Main function to interact with the user."""
#     product_options = list(PRODUCT_DATA.keys())
#     selected_products = {}

#     print("Select up to 4 products:")
#     for i in range(4):
#         product = get_user_input(f"Select product {i + 1} (or press Enter to skip):", product_options)
#         if not product:
#             break
#         while True:
#             try:
#                 amount = float(input(f"Enter the amount (kg) for {product}: "))
#                 break
#             except ValueError:
#                 print("Invalid input. Please enter a numeric value.")
#         selected_products[product] = amount

#     print("\nIndividual Nutrient Breakdown:")
#     for product, amount in selected_products.items():
#         print(f"\n{product} ({amount} kg):")
#         results = calculate_nutrient_breakdown(product, amount)
#         print(f"{'Nutrient':<15}{'kg/ha':<10}{'ppm':<10}")
#         for row in results:
#             print(f"{row['Nutrient']:<15}{row['kg/ha']:<10.2f}{row['ppm']:<10.2f}")

#     print("\nCombined Nutrient Breakdown:")
#     combined_results = calculate_combined_nutrient_breakdown(selected_products)
#     print(f"{'Nutrient':<15}{'kg/ha':<10}{'ppm':<10}")
#     for row in combined_results:
#         print(f"{row['Nutrient']:<15}{row['kg/ha']:<10.2f}{row['ppm']:<10.2f}")

# if __name__ == "__main__":
#     main()




