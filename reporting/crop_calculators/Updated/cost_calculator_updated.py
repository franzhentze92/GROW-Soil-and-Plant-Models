import sys
import subprocess

# ✅ Automatically install `tabulate` if not found
try:
    from tabulate import tabulate
except ModuleNotFoundError:
    print("\n📌 'tabulate' module not found. Installing now...\n")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
    from tabulate import tabulate  # Import again after installation

# ✅ Conversion factors for land-based applications (Includes mL/Ha and g/Ha)
CONVERSION_FACTORS = {
    "L/Ha": 1, "Kg/Ha": 1, "Ton/Ha": 1000, "mL/Ha": 0.001, "g/Ha": 0.001,
}

# ✅ Area conversion factors (No Acres)
AREA_CONVERSION_FACTORS = {
    "Hectares": 1,
    "Liters of Water": 1  # No conversion needed for water applications
}

# ✅ Product price data
PRODUCT_PRICES = {
    "K-Rich™": { "1 L": 33.95, "5 L": 87.5, "20 L": 260.6 },
    "Cal-Tech™": { "5 L": 68.5, "20 L": 196.2 },
    "Calcium Fulvate™": { "20 L": 115.85 },
    "Citrus-Tech Triple Ten™": { "5 L": 85, "20 L": 259.55 },
    "Cloak Spray Oil™": { "1 L": 31.4, "5 L": 86, "20 L": 259.55 },
    "Nutri-Carb-N ™": { "5 L": 41.15, "20 L": 106.05 },
    "Phos-Force™": { "5 L": 88.6, "20 L": 287.35 },
    "Photo-Finish™": { "1 L": 28.8, "5 L": 76.15, "20 L": 233.3 },
    "Potassium Silicate™": { "5 L": 87.5, "20 L": 228.65 },
    "Seed-Start™": { "1 L": 14.35, "5 L": 37.6, "20 L": 107.65 },
    "Trio (CMB)™": { "5 L": 53.55, "20 L": 155.55 },
    "Triple Ten™": { "1 L": 30.85, "5 L": 84.4, "20 L": 258.55 },
    "Tsunami™ Super Spreader": { "5 L": 231.75, "20 L": 739.55 },
    "Activated Char Condensate (ACC)™": { "1 L": 23.65, "5 L": 55.55, "20 L": 159.6 },
    "Aloe-Tech™": { "5 L": 67.45, "20 L": 187.4 },
    "Amino-Max™": { "1 L": 35.55, "5 L": 85, "20 L": 254.95 },
    "Brix-Fix™": { "5 L": 47.9, "20 L": 133.9 },
    "Nutri-Kelp™": { "5 KG": 226.6, "20 KG": 777.65 },
    "Nutri-Sea Liquid Fish™": { "1 L": 22.15, "5 L": 49.4, "20 L": 134.9 },
    "Nutri-Stim Saponins™": { "10 L": 250.8 },
    "Nutri-Stim Triacontanol™": { "1 L": 115.35, "5 L": 410.95, "20 L": 1297.8 },
    "Nutri-Tech Black Gold®": { "1 L": 25.7, "5 L": 57.65, "20 L": 162.25 },
    "Root & Shoot™": { "1 L": 34.5, "5 L": 83.95, "20 L": 250.3 },
    "SeaChange KFF™": { "5 L": 50.4, "20 L": 142.15 },
    "SeaChange Liquid Kelp™": { "5 L": 58.65, "20 L": 164.75 },
    "Tri-Kelp™": { "1 KG": 43.2, "5 KG": 137.95, "20 KG": 439.8 },
    "Nutri-Key Boron Shuttle™": { "5 L": 57.65, "20 L": 167.85 },
    "Nutri-Key Calcium Shuttle™": { "5 L": 79.85, "20 L": 233.8 },
    "Nutri-Key Cobalt Shuttle™": { "1 L": 39.65, "5 L": 169.95 },
    "Nutri-Key Copper Shuttle™": { "5 L": 88.05, "20 L": 257.5 },
    "Nutri-Key Hydro-Shuttle™": { "5 L": 141.65, "20 L": 444.95 },
    "Nutri-Key Iron Shuttle™": { "5 L": 63.8, "20 L": 179.2 },
    "Nutri-Key Magnesium Shuttle™": { "5 L": 61.75, "20 L": 180.2 },
    "Nutri-Key Manganese Shuttle™": { "5 L": 75.15, "20 L": 223.5 },
    "Nutri-Key Moly Shuttle™": { "5 L": 157.1, "20 L": 496.45 },
    "Nutri-Key Shuttle Seven™": { "5 L": 70, "20 L": 200.8 },
    "Nutri-Key Zinc Shuttle™": { "5 L": 87.05, "20 L": 264.2 },
    "Boron Essentials™": { "5 L": 27.75, "20 L": 68.5 },
    "Copper Essentials™": { "5 L": 54.1, "20 L": 160.15 },
    "Iron Essentials™": { "5 L": 37.05, "20 L": 124.1 },
    "Manganese Essentials™": { "5 L": 50.4, "20 L": 136.95 },
    "Multi-Boost™": { "20 L": 144.3 },
    "Multi-Min™": { "20 L": 131.35 },
    "Multi-Plex™": { "20 L": 186.95 },
    "Zinc Essentials™": { "5 L": 40.7, "20 L": 132.8 },
    "CalMag-Life Organic™": { "5 L": 34.95, "15 L": 79.25 },
    "Dia-Life Organic™": { "5 L": 40.1, "15 L": 89.55 },
    "Gyp-Life Organic™": { "5 L": 38.05, "15 L": 85.45 },
    "Lime-Life Organic™": { "5 L": 36, "15 L": 80.3 },
    "Mag-Life Organic™": { "5 L": 36.55, "15 L": 88.05 },
    "Phos-Life Organic™": { "5 L": 56.6, "15 L": 133.85 },
    "Sili-Cal (B)™": { "5 L": 38.7, "15 L": 86.75 },
    "Life Force® Carbon™": { "30 L": 24.20 },
    "Life Force® Gold Pellets™": { "25 KG": 33.50 },
    "NTS Soft Rock™": { "25 KG": 44.80 },
    "Nutri-Gyp™ Natural Gypsum": { "25 KG": 41.15 },
    "Nutri-Phos Super Active™": { "25 KG": 108.30 },
    "NTS Fast Fulvic™": { "5 L": 37.05, "20 L": 95.75 },
    "NTS Fulvic Acid Powder™": { "5 KG": 94.25, "20 KG": 293.55 },
    "NTS FulvX™ Powder": { "5 KG": 60.50, "25 KG": 226.65 },
    "NTS Liquid Humus™": { "5 L": 27.30, "20 L": 66.90 },
    "NTS Soluble Humate Granules™": { "25 KG": 95.75 },
    "NTS Stabilised Boron Granules™": { "25 KG": 121.50 },
    "NTS Super Soluble Humates™": { "25 KG": 163.70 },
    "CalMag-Life Organic™": { "5 L": 34.95, "15 L": 79.25 },
    "Dia-Life Organic™": { "5 L": 40.1, "15 L": 89.55 },
    "Gyp-Life Organic™": { "5 L": 38.05, "15 L": 85.45 },
    "Lime-Life Organic™": { "5 L": 36, "15 L": 80.3 },
    "Mag-Life Organic™": { "5 L": 36.55, "15 L": 88.05 },
    "Phos-Life Organic™": { "5 L": 56.6, "15 L": 133.85 },
    "Sili-Cal (B)™": { "5 L": 38.7, "15 L": 86.75 },
    "Life Force® Carbon™": { "30 L": 24.20 },
    "Life Force® Gold Pellets™": { "25 KG": 33.50 },
    "NTS Soft Rock™": { "25 KG": 44.80 },
    "Nutri-Gyp™ Natural Gypsum": { "25 KG": 41.15 },
    "Nutri-Phos Super Active™": { "25 KG": 108.30 },
    "NTS Fast Fulvic™": { "5 L": 37.05, "20 L": 95.75 },
    "NTS Fulvic Acid Powder™": { "5 KG": 94.25, "20 KG": 293.55 },
    "NTS FulvX™ Powder": { "5 KG": 60.50, "25 KG": 226.65 },
    "NTS Liquid Humus™": { "5 L": 27.30, "20 L": 66.90 },
    "NTS Soluble Humate Granules™": { "25 KG": 95.75 },
    "NTS Stabilised Boron Granules™": { "25 KG": 121.50 },
    "NTS Super Soluble Humates™": { "25 KG": 163.70 },
    "Nutri-Life B.Sub™": { "1 L": 74.10, "5 L": 293.05 },
    "Nutri-Life BAM™": { "1 L": 13.35, "5 L": 25.70, "20 L": 97.80 },
    "Nutri-Life Bio-N™": { "1 L": 70.00, "5 L": 279.65 },
    "Nutri-Life Bio-Plex™": { "1 L": 72.60, "5 L": 287.35 },
    "Nutri-Life Bio-P™": { "1 L": 77.75, "5 L": 279.65 },
    "Nutri-Life Micro-Force™": { "0.25 KG": 98.85, "0.5 KG": 170.45, "1 KG": 299.75, "3 KG": 808.55, "7 KG": 1874.60, "20 KG": 4881.15 },
    "Nutri-Life Myco-Force™": { "1 KG": 44.25, "5 KG": 173.00 },
    "Nutri-Life Platform®": { "1 KG": 112.25, "10 KG": 1014.55 },
    "Nutri-Life Root-Guard™": { "5 KG": 176.65 },
    "Nutri-Life Tricho-Shield™": { "0.2 KG": 20.55, "1 KG": 56.60, "5 KG": 250.30 },
    "Urea (Source locally)": { "25 KG": 0 },
    "Sodium Molybdate (Source locally)": { "25 KG": 0 },
    "Soluble Boron (Source locally)": { "25 KG": 0 },
    "Calcium Nitrate (Source locally)": { "25 KG": 0 },
    "MAP (Source locally)": { "25 KG": 0 },
    "DAP (Source locally)": { "25 KG": 0 },
    "Potassium Sulfate (Source locally)": { "25 KG": 0 },
    "Magnesium Sulfate (Source locally)": { "25 KG": 0 },
    "Ammonium Sulfate (Source locally)": { "25 KG": 0 },
    "Iron Sulfate (Source locally)": { "25 KG": 0 },
    "Manganese Sulfate (Source locally)": { "25 KG": 0 },
    "Copper Sulfate (Source locally)": { "25 KG": 0 },
    "Zinc Sulfate (Source locally)": { "25 KG": 0 },
    "MKP (Source locally)": { "25 KG": 0 },
    "Chicken Manure (Source locally)": { "25 KG": 0 },
    "Worm Juice (Source locally)": { "20 L": 0 },
    "Elemental Sulfur (Source locally)": { "25 KG": 0 },
    "Dolomite (Source locally)": { "25 KG": 0 },
    "Lime (Source locally)": { "25 KG": 0 },
    "Gypsum (Source locally)": { "25 KG": 0 },
    "Magnesite (Source locally)": { "25 KG": 0 },
    "Potassium Nitrate (Source locally)": { "25 KG": 0 },
    "Borax (Source locally)": { "25 KG": 0 },
    "Magnesium Oxide (Source locally)": { "25 KG": 0 }
}

# ✅ Function to convert rate for land-based applications
def convert_rate_to_base(rate, unit):
    """Convert the input rate to the base unit (L/Ha)."""
    if unit not in CONVERSION_FACTORS:
        raise ValueError(f"Unit {unit} is not supported.")
    return rate * CONVERSION_FACTORS[unit]

# ✅ Function to calculate cost for water-based applications
def calculate_cost_for_water(product, size, rate_per_liter, total_water_volume):
    """Calculate cost for a water-based application using L of product per L of water."""
    product_data = PRODUCT_PRICES.get(product, {})

    if not product_data or size not in product_data:
        print(f"Warning: No data found for {product} with size {size}. Defaulting to $0.")
        return 0  # Prevent errors

    # ✅ Convert package price to per-liter price
    package_size = float(size.split()[0])  # Extract numeric part of size (e.g., "5 L" -> 5)
    price_per_liter = product_data[size] / package_size  # Get per-liter cost

    # ✅ Calculate total product needed
    total_product_needed = rate_per_liter * total_water_volume

    # ✅ Calculate total cost
    total_cost = total_product_needed * price_per_liter
    return total_cost

# ✅ Function to calculate total cost for all applications
def calculate_total_cost(product, size, rate, unit, area, area_unit):
    """Calculate the total cost for land or water-based applications."""

    if area_unit == "Liters of Water":
        total_cost = calculate_cost_for_water(product, size, rate, area)  # Water application
        cost_per_unit = total_cost / area  # Cost per L of water
    else:
        area_in_base_unit = area / AREA_CONVERSION_FACTORS[area_unit]  # Convert hectares
        rate_in_base_unit = convert_rate_to_base(rate, unit)
        product_data = PRODUCT_PRICES.get(product, {})

        if not product_data or size not in product_data:
            print(f"Warning: No data found for {product} with size {size}. Defaulting to $0.")
            return 0  # Prevent errors

        package_size = float(size.split()[0])  # Extract numeric part of size (e.g., "5 L" -> 5)
        price_per_liter = product_data[size] / package_size  # Get per-liter cost

        cost_per_unit = rate_in_base_unit * price_per_liter
        total_cost = cost_per_unit * area_in_base_unit

    breakdown = {
        "Product": product,
        "Size": size,
        "Rate": rate,
        "Rate Unit": unit,
        "Cost per Hectare/Water Unit": f"${cost_per_unit:.2f}",
        "Total Cost": f"${total_cost:.2f}"
    }

    return total_cost, breakdown

# ✅ Function to get user input from a list of options
def get_user_input(prompt_message, options):
    """Provide a simple input mechanism as an alternative to dropdowns."""
    print(f"\n{prompt_message}")
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

# ✅ **Main function**
def main():
    """Main function to interact with the user."""
    product_options = list(PRODUCT_PRICES.keys())
    unit_options = list(CONVERSION_FACTORS.keys()) + ["L of product per L of water"]
    area_unit_options = ["Hectares", "Liters of Water"]  # Removed Acres

    print("\nSelect a product:")
    product = get_user_input("Choose a product:", product_options)

    # ✅ Dynamically fetch available sizes for the selected product
    size_options = list(PRODUCT_PRICES[product].keys())
    size = get_user_input(f"Select the size for {product}:", size_options)

    rate = float(input(f"Enter the application rate ({unit_options[-1]} for water or select unit for land): "))
    rate_unit = get_user_input("Select the rate unit:", unit_options)

    area = float(input("\nEnter the total area (Hectares) or total volume (Liters of Water): "))
    area_unit = get_user_input("Select the unit for the area:", area_unit_options)

    print(
        "\n\nproduct: " + str(product) + 
        "\nsize: " + str(size) + 
        "\nrate: " + str(rate) + 
        "\nrate_unit: " + str(rate_unit) + 
        "\narea: " + str(area) + 
        "\narea_unit: " + str(area_unit)
    )

    total_cost, breakdown = calculate_total_cost(product, size, rate, rate_unit, area, area_unit)

    print("\nCost Breakdown:")
    headers = ["Product", "Size", "Rate", "Rate Unit", "Cost per Hectare/Water Unit", "Total Cost"]
    print(tabulate([list(breakdown.values())], headers=headers, tablefmt="grid"))

    print(f"\nTotal Cost: ${total_cost:.2f}")

# ✅ Run the script
if __name__ == "__main__":
    main()


# product: K-Rich™
# size: 1 L
# rate: 1.0
# rate_unit: L/Ha
# area: 11.0
# area_unit: Hectares

