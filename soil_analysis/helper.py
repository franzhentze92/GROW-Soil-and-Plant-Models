from collections import defaultdict
from soil_analysis.models import (
    BaseSaturationAcceptableValues, 
    BaseSaturationHighTecValues,
    ConversionFactor,
    ChemicalProperty
)
import pprint

# Fixed matrix for TEC values
tec_matrix = [
    {"min": 1.0, "max": 3.0, "ratio": 3.0, "Ca": 60.0, "Mg": 20.0, "K": (5.0, 7.0)},
    {"min": 3.0, "max": 5.0, "ratio": 3.4, "Ca": 62.0, "Mg": 18.0, "K": (5.0, 7.0)},
    {"min": 5.0, "max": 7.0, "ratio": 4.0, "Ca": 64.0, "Mg": 16.0, "K": (4.0, 5.0)},
    {"min": 7.0, "max": 9.0, "ratio": 4.3, "Ca": 65.0, "Mg": 15.0, "K": (3.5, 5.0)},
    {"min": 9.0, "max": 11.0, "ratio": 5.2, "Ca": 67.0, "Mg": 13.0, "K": (3.0, 5.0)},
    {"min": 11.0, "max": 30.0, "ratio": 5.7, "Ca": 68.0, "Mg": 12.0, "K": (3.0, 5.0)},
    {"min": 30.0, "max": 100000.0, "ratio": 7.0, "Ca": 70.0, "Mg": 10.0, "K": (2.0, 5.0)},
]

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


def process_cell_text(cell, blocks_dict):
    """Extract text from a cell using its word relationships."""
    if "Relationships" not in cell:
        return ""
        
    word_ids = [
        word_id
        for r in cell["Relationships"] 
        if r["Type"] == "CHILD"
        for word_id in r["Ids"]
    ]
    return " ".join(
        blocks_dict[word_id]["Text"]
        for word_id in word_ids
        if word_id in blocks_dict
    )

def process_table_cells(table, blocks_dict):
    """Process all cells in a table and return structured row data."""
    rows = {}
    
    for rel in table.get("Relationships", []):
        if rel["Type"] != "CHILD":
            continue
            
        for cell_id in rel["Ids"]:
            cell = blocks_dict.get(cell_id)
            if not cell or cell["BlockType"] != "CELL":
                continue
            
            row_idx, col_idx = cell["RowIndex"], cell["ColumnIndex"]
            text = process_cell_text(cell, blocks_dict)
            
            if row_idx not in rows:
                rows[row_idx] = {}
            rows[row_idx][col_idx] = text
            
    return rows

def build_table_matrix(rows):
    """Convert row dictionary into a 2D matrix."""
    if not rows:
        return []
        
    max_row = max(rows.keys())
    max_col = max(max(row.keys(), default=0) for row in rows.values())
    
    return [
        [rows.get(r, {}).get(c, "") for c in range(1, max_col + 1)]
        for r in range(1, max_row + 1)
    ]

def extract_table_data(response):
    """Main function to extract and organize table data from the response."""
    # Pre-calculate blocks dictionary and page grouping
    blocks = response["Blocks"]
    blocks_dict = {block["Id"]: block for block in blocks}
    page_blocks = defaultdict(list)
    page_tables = defaultdict(list)
    
    # Group blocks by page in one pass
    for block in blocks:
        if block["BlockType"] == "TABLE":
            page_blocks[block["Page"]].append(block)
    
    # Process each page
    for page, tables in page_blocks.items():
        for table in tables:
            rows = process_table_cells(table, blocks_dict)
            table_data = build_table_matrix(rows)
            if table_data:
                page_tables[page].append(table_data)

    return page_tables


def format_table_data(page_tables):
    formatted_output = []
    for page_num, tables in page_tables.items():
        formatted_output.append(f"\n=== Page {page_num} ===")
        for table_idx, table in enumerate(tables, 1):
            formatted_output.append(f"\nTable {table_idx}:")
            formatted_output.append("\n".join(["\t".join(row) for row in table]))
    return "\n".join(formatted_output)

def get_acceptable_values(crop_id, symbol, tec):
    # print(f"\nLooking up values for {symbol} with TEC={tec}")

    # First, let's check if the chemical property exists
    chemical_property = ChemicalProperty.objects.filter(symbol=symbol).first()
    # print(f"Found chemical property: {chemical_property}")
    
    if tec > 4:
        # Add detailed query debugging
        query = BaseSaturationHighTecValues.objects.filter(
            crop_id=crop_id,
            chemical_property__symbol=symbol
        )
        # print(f"Query SQL: {query.query}")
        record = query.first()
        # k_record = BaseSaturationHighTecValues.objects.get(
        #     crop_id=crop_id,
        #     chemical_property__symbol='K'
        # )
        # print(k_record,"======================900000000000000000000")
        # # Check all records for this crop
        all_records = BaseSaturationHighTecValues.objects.filter(crop_id=crop_id)
        # print("All records for this crop:")
        # for r in all_records:
        #     print(f"- {r.chemical_property.symbol}: {r.chemical_property.name}")

    else:
        query = BaseSaturationAcceptableValues.objects.filter(
            crop_id=crop_id,
            chemical_property__symbol=symbol
        )
        # print(f"Query SQL: {query.query}")
        record = query.first()
    
    if record:
        # Ensure upper value is greater than lower value
        lower = min(record.lower_value, record.upper_value)
        upper = max(record.lower_value, record.upper_value)
        # print(f"Found values: lower={lower}, upper={upper}")
        return lower, upper
    else:
        # print(f"No values found for {symbol}")
        return 0, 0

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

def calculate_cec(ca_cmol, mg_cmol, k_cmol, na_cmol, al_cmol):
    return ca_cmol + mg_cmol + k_cmol + na_cmol + al_cmol

def calculate_base_saturation(crop_id, ppm_values):
    """
    Calculate base saturation percentages for soil nutrients.
    """
    # Step 1&2: Convert PPM to MEQ using factors from database    
    meq_values = {} # cmol(+)/kg (centimoles of charge per kilogram) 
    for nutrient in ['Ca', 'Mg', 'K', 'Na', 'Al', 'pH']:
        if nutrient not in ppm_values:
            print(f"Warning: {nutrient} not found in ppm_values")
            continue
            
        conversion_factor = ConversionFactor.objects.filter(
            crop_id=crop_id,
            nutrient=nutrient
        ).first()
        
        if not conversion_factor:
            # print(f"Warning: No conversion factor found for {nutrient} in crop_id={crop_id}")
            continue
        
        # print(f"Processing {nutrient}: {ppm_values[nutrient]} PPM, Conversion factor: {conversion_factor.factor}")
        
        meq_values[nutrient] = get_meq_value(ppm_values[nutrient], conversion_factor.factor)
        # print(f"Converted {nutrient}: {ppm_values[nutrient]} PPM -> {meq_values[nutrient]} MEQ")  # Debug print

    # Step 2.2: Calculate pH value
    ph_value = float(ppm_values.get('pH', 7.0))  # Default to 7.0 if pH not provided
    ph_value = min(ph_matrix.keys(), key=lambda x: abs(x - ph_value))    
    # print(ph_value, ppm_values.get('pH', 7.0), "==========ph===========")

    hydrogen_percentage, other_bases_percentage = ph_matrix[ph_value]
    # print(f"Hydrogen percentage: {hydrogen_percentage}, Other bases percentage: {other_bases_percentage}")
    
    # Step 3: Calculate CEC (sum of base cations)
    cec = calculate_cec(
        meq_values.get('Ca', 0),    meq_values.get('Mg', 0), 
        meq_values.get('K', 0),     meq_values.get('Na', 0),
        meq_values.get('Al', 0)
    )
    # print(f"Calculated CEC: {cec}")

    # Step 4: Calculating Total Exchangeable Cations (TEC)
    # Using the calculate_obresult() function to calculate the Total Exchangeable Cations (TEC)
    hydrogen_cmol, other_bases_cmol, tec = calculate_obresult(
        hydrogen_percentage, other_bases_percentage, cec
    )
    # print(f"TEC: {tec}")

    # Step 5: Base Saturation Calculation
    # Note that those are the percentages
    base_saturation_percentages = {
        'Ca': (meq_values.get('Ca', 0) / tec) * 100 if tec else 0,
        'Mg': (meq_values.get('Mg', 0) / tec) * 100 if tec else 0,
        'K': (meq_values.get('K', 0) / tec) * 100 if tec else 0,
        'Na': (meq_values.get('Na', 0) / tec) * 100 if tec else 0,
        'Al': (meq_values.get('Al', 0) / tec) * 100 if tec else 0,
        "H": hydrogen_percentage,
    }

    base_saturation_percentages["OB"] = max(0, 100 - sum(base_saturation_percentages.values()))

    # print("Base Saturation Percentages:")
    # pprint.pp(base_saturation_percentages)

    # Step 6: Ideal Ranges for Base Saturation and PPM
    # Build the final base saturation dictionary
    base_saturation = {}
    ideal_values_to_show = {}

    nutrient_full_names = {
        'Ca': 'Calcium',    'Mg': 'Magnesium',
        'K': 'Potassium',   'Na': 'Sodium',
        'H': 'Hydrogen',    'OB': 'Other Bases',
        'Al': 'Aluminium',  'pH': 'pH'
    }
    ideal_ranges = {
        "Al": (0.375, 0.625),     "H": (7.5, 12.5), 
        "OB": (None, 5)
    }

    for entry in tec_matrix:
        if entry["min"] <= tec < entry["max"]:
            ideal_ca_mg_ratio = entry["ratio"]
            
            if tec < 4:
                ideal_ranges["Ca"] = (46.5, 77.5)
                ideal_ranges["Mg"] = (13.5, 22.5)
                ideal_ranges["K"] = (5.0, 7.0)
                # ideal_ranges["Al"] = (0.0, 2.0) // client requested to update this later
                
                ideal_values_to_show["Ca"] = 62.0
                ideal_values_to_show["Mg"] = 18.0

            else:
                ideal_ranges["Ca"] = (entry["Ca"] * 0.7515, entry["Ca"] * 1.25)
                ideal_ranges["Mg"] = (entry["Mg"] * 0.7515, entry["Mg"] * 1.25)
                ideal_ranges["K"] = entry["K"]
                
                ideal_values_to_show["Ca"] = (ideal_ranges["Ca"][0] + ideal_ranges["Ca"][1]) / 2
                ideal_values_to_show["Mg"] = (ideal_ranges["Mg"][0] + ideal_ranges["Mg"][1]) / 2

            ideal_ranges["Na"] = (0.5, 1.5)
            ideal_values_to_show["K"] = entry["K"]
            ideal_values_to_show["Na"] = 1.0

            ideal_values_to_show["H"] = (ideal_ranges["H"][0] + ideal_ranges["H"][1]) / 2
            ideal_values_to_show["Al"] = (ideal_ranges["Al"][0] + ideal_ranges["Al"][1]) / 2
            break

    # This computes the percentages for each nutrient and rounds them to 2 decimal places
    # Not paired to any other nutrients outside of the base nutrients 
    for nutrient, percentage in base_saturation_percentages.items():
        if nutrient in ['Ca', 'Mg', 'K', 'Na', 'H', 'OB', 'Al']:
            lower, upper = get_acceptable_values(crop_id, nutrient, tec)
            value = percentage
            
            if nutrient in ideal_ranges or nutrient in ["Ca", "Mg", "H", "Al"]:
                lower, upper = ideal_ranges.get(nutrient, (0, 0))

                if nutrient in ["Ca", "Mg", "H", "Al"]:
                    # here we show a single value for the range,
                    lower, upper = None, ideal_values_to_show.get(nutrient)

            # print(f"Calculating {nutrient}: value={value}, lower={lower}, upper={upper}")

            base_saturation[nutrient] = {
                'value': f"{round(value, 2):.2f}" if value else "0.00",
                'lower': f"{round(lower, 1):.2f}" if (lower or lower == 0) else None,
                'upper': f"{round(upper, 1):.2f}" if (upper or upper == 0) else None,
                'deficient': f"{round(lower / 1.5, 1):.2f}" if lower else "0.00",
                'excessive': f"{round(upper * 1.5, 1):.2f}" if upper else "0.00",
                'full_name': nutrient_full_names.get(nutrient, nutrient)
            }

    return base_saturation, round(tec, 2), round(cec, 2), meq_values

def get_ratio(ppm_values, nutrient1, nutrient2):
    """Calculate ratio between two nutrients using conversion factors from database"""
    meq_values = {}
    
    # Get conversion factors from database for both nutrients
    for nutrient in [nutrient1, nutrient2]:
        conversion_factor = ConversionFactor.objects.filter(
            nutrient=nutrient
        ).first()
        
        if conversion_factor:
            meq_values[nutrient] = get_meq_value(ppm_values[nutrient], conversion_factor.factor)
        else:
            print(f"Warning: No conversion factor found for {nutrient}")
            meq_values[nutrient] = 0
    
    nutrient1_meq = meq_values.get(nutrient1, 0)
    nutrient2_meq = meq_values.get(nutrient2, 0)
    
    return round(nutrient1_meq/nutrient2_meq, 2) if nutrient2_meq else 0


def get_meq_value(value, divide_by):
    """
    Converts a PPM (parts per million) value to MEQ (milliequivalent) value by dividing by a conversion factor.
    
    Args:
        value (float/str): The PPM value to convert (can be string or numeric)
        divide_by (float): The conversion factor to divide by
        
    Returns:
        float: The calculated MEQ value, or 0 if conversion fails
    """
    try:
        # Handle string values that might contain commas
        if isinstance(value, str):
            # Replace comma with dot for decimal values
            value = value.replace(',', '.')
            # Remove any leading/trailing whitespace
            value = value.strip()
            # Handle values with '<' or '>' symbols
            if value.startswith(('<', '>')):
                value = value[1:].strip()
        
        # Convert to float and perform division
        numeric_value = float(value)
        if divide_by == 0:  # Prevent division by zero
            return 0
        return numeric_value / divide_by
        
    except (ValueError, TypeError):
        # Return 0 if conversion fails or any other error occurs
        return 0