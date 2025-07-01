import csv
import io
import requests
from datetime import datetime
import boto3
from crops.models import Crop, ChemicalProperty, CropAcceptabelValues
from soil_analysis.models import (
    SoilAcceptableValues,
    LamotteAcceptableValues,
    TaeAcceptableValues,
)
from django.conf import settings
from openai import OpenAI
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import Http404

""" AWS Configurations """
aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
aws_region = settings.AWS_REGION
s3_bucket = settings.S3_RESPONSE_BUCKET
s3_csv_bucket = settings.S3_CSV_BUCKET

# Initialize OpenAI client with error handling
try:
    client = OpenAI()
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    print("Setting OPENAI_API_KEY environment variable...")
    import os
    os.environ.setdefault('OPENAI_API_KEY', 'dummy_key_for_development')
    client = OpenAI()

# Creating AWS Boto3 Session
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)
textract_client = session.client("textract")
s3 = session.client("s3")

def generate_recommendations_summary(context):
    # Prepare the prompt
    # The prompt structure should be:
    # 1. Goal
    # 2. Return Format (and example -- might not consider the example if it's too long)
    # 3. Warnings
    # 4. Context Dump

    # The prompt will only summarize the nutrients explanation for all nutrients paragraphs
    # We can extract the recommended products and return them in a dict format
    prompt = f"""I am a farmer who needs help with fertilization recommendations. 
    I have nutrients deficiency and excess details for my crop analysis.

    ### Goal
    - I need you to summarise the given nutrients details in the context in a structured and meaningful way 
    to know nutrient explanations for both deficient and excess nutrients in 1-2 paragraphs. 

    ### Return Format
    - Combined Nutrient Explanation, both nutrients deficient and excess details must be mentioned, in 1-2 paragraphs maximum.
    - All deficiencies and excess nutrients in the context must be included in the output.
    - For example, sentences to use: "Your leaf test results indicate a ... In fruit trees, ... deficiency leads to ..., 
    ultimately lowering ... Meanwhile, excess ... disrupts ..., weakening ..., reducing ..., and increasing ... Addressing 
    these imbalances is essential for sustaining healthy growth and improving fruit quality.".
    - If no context information found at all, return the following text: "All nutrients are within the acceptable range.".

    ### Warnings
    - The explanations should be clear and concise.
    - The recommendations summary should be specific to the given context, don't provide information or summary out of context.
    - If the nutrient is mentioned as excess in the context, it should also be mentioned as excess in the output, and same for 
    the deficient. Make sure that they are not changed in the output. They are usually categorized by the first line, for example:
    "Nitrogen Excess Explanation" means nitrogn is excess.

    ### Context Dump Start
    {context}
    ### Context Dump Ends
    """

    # Model call
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful farmer assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content

def load_recommendations_excel_data(deficiencies_file, excesses_file, product_recommendations_file):
    """ Load deficiency, excess, and recommendation data from Excel files and standardize column names. """
    deficiencies_df = pd.read_excel(deficiencies_file)
    excesses_df = pd.read_excel(excesses_file)
    recommendations_df = pd.read_excel(product_recommendations_file, sheet_name="Hoja1")

    # Standardize column names (strip spaces and convert to lowercase)
    deficiencies_df.columns = deficiencies_df.columns.str.strip().str.lower()
    excesses_df.columns = excesses_df.columns.str.strip().str.lower()
    recommendations_df.columns = recommendations_df.columns.str.strip().str.lower()

    return deficiencies_df, excesses_df, recommendations_df

def get_nutrient_explanation(nutrient, crop_type, df):
    """ Extracts the explanation for a specific nutrient from the given DataFrame. """
    nutrient = nutrient.strip()
    crop_type = crop_type.strip()
    
    explanation = df[(df["nutrient"].str.strip() == nutrient) & (df["crop type"].str.strip() == crop_type)]
    
    if not explanation.empty:
        return explanation.iloc[0]["explanation"]
    else:
        return f"No explanation found for {nutrient} in {crop_type}."

def get_products_recommendations(nutrient, crop_type, application_method, recommendation_type, df):
    """ Retrieves product recommendations from the Excel dataset. """
    nutrient = nutrient.strip()
    crop_type = crop_type.strip()
    application_method = application_method.strip()
    recommendation_type = recommendation_type.strip()
    
    recommendation = df[
        (df["nutrient"].str.strip() == nutrient) & 
        (df["crop type"].str.strip() == crop_type) & 
        (df["fertilization equipment"].str.strip() == application_method) & 
        (df["fertilization type"].str.strip() == recommendation_type)
    ]

    if not recommendation.empty:
        products = recommendation.iloc[0][["product 1", "product 2", "product 3", "product 4"]].dropna().tolist()
        return products if products else ["No specific product found in database."]
    return ["No specific product found in database."]

def extract_table_data(response):
    blocks = response["Blocks"]
    table_data = []

    for block in blocks:
        if block["BlockType"] == "TABLE":
            rows = {}
            for relationship in block["Relationships"]:
                if relationship["Type"] == "CHILD":
                    for id in relationship["Ids"]:
                        cell = next(b for b in blocks if b["Id"] == id)
                        if cell["BlockType"] == "CELL":
                            row_index = cell["RowIndex"]
                            col_index = cell["ColumnIndex"]
                            text = ""
                            if "Relationships" in cell:
                                text = " ".join(
                                    [
                                        b["Text"]
                                        for b in blocks
                                        if b["Id"]
                                        in [
                                            r["Ids"][0]
                                            for r in cell["Relationships"]
                                            if r["Type"] == "CHILD"
                                        ]
                                    ]
                                )
                            rows.setdefault(row_index, {}).setdefault(col_index, "")
                            rows[row_index][col_index] = text

            max_row = max(rows.keys())
            max_col = max(max(rows[r].keys()) for r in rows)
            for r in range(1, max_row + 1):
                row_data = [rows.get(r, {}).get(c, "") for c in range(1, max_col + 1)]
                table_data.append(row_data)

    return table_data


def upload_to_s3(table_data, file_key):
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(table_data)
    s3.put_object(Body=csv_buffer.getvalue(), Bucket=s3_csv_bucket, Key=file_key)
    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": s3_csv_bucket, "Key": file_key}, ExpiresIn=3600
    )
    return presigned_url


def get_farmer_details(response):
    data = {"NAME": "", "ADDRESS": "", "SAMPLE_REC": "", "LAND_USE": ""}

    blocks = response["Blocks"]
    field_mapping = {
        "INTERESADO:": "NAME",
        "PROCEDENCIA:": "ADDRESS",
        "FECHA DE INGRESO:": "SAMPLE_REC",
        "CULTIVO:": "LAND_USE",
    }

    column_keys = set(field_mapping.keys())

    for index, block in enumerate(blocks):
        if block["BlockType"] == "LINE":
            text = block["Text"].strip()
            parts = text.split(":", 1)
            key = parts[0] + ":"
            if key in column_keys:
                value = parts[1].strip() if len(parts) > 1 else ""
                if not value and index + 1 < len(blocks):
                    next_block_text = blocks[index + 1]["Text"].strip()
                    if next_block_text not in column_keys:
                        value = next_block_text
                data[field_mapping[key]] = value

    return data


# Function to upload a PDF file to S3 and return a presigned URL
def upload_pdf_file_to_s3(file, file_name):
    s3.upload_fileobj(file, s3_bucket, file_name)
    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": s3_bucket, "Key": file_name}, ExpiresIn=3600
    )
    return presigned_url


# OCR Function
def get_ocr(image_bytes):
    response = textract_client.analyze_document(
        Document={"Bytes": image_bytes}, FeatureTypes=["TABLES"]
    )
    return response


# Function to read CSV from a presigned URL
def read_csv_from_presigned_url(presigned_url):
    response = requests.get(presigned_url)
    response.raise_for_status()
    csv_buffer = io.StringIO(response.text)
    return list(csv.reader(csv_buffer))


# Process crop data
def process_crop_data(file, crop_id):
    image_bytes = file.read()
    crop_instance = Crop.objects.filter(id=crop_id).first()
    response = get_ocr(image_bytes)
    data = get_farmer_details(response)
    result = []

    # Extract table data and upload to S3
    table_data = extract_table_data(response)
    current_time = datetime.now()
    output_csv = f"{current_time}.csv"
    presigned_url = upload_to_s3(table_data, output_csv)
    csv_data = read_csv_from_presigned_url(presigned_url)

    acceptable_value = None

    if len(csv_data) <= 1 or not all(
        cell == "" or cell == "%" or cell == "Ppm" for cell in csv_data[0]
    ):
        print("Not enough data to process")
        return {"farmer_data": data, "result": result}

    # Process CSV data
    csv_data = csv_data[1:]
    headers = csv_data[0]
    identifications = [
        {headers[i]: row[i] for i in range(len(headers))} for row in csv_data[1:]
    ]
    last_identification = identifications[-1]

    if last_identification.get("Na"):
        last_identification["Na"] = str(float(last_identification["Na"]) / 10000)

    for nutrient in headers[1:]:
        chemical_property_instance = ChemicalProperty.objects.filter(
            symbol=nutrient
        ).first()
        acceptable_value = CropAcceptabelValues.objects.filter(
            crop=crop_instance, chemical_property=chemical_property_instance
        ).first()
        value = last_identification.get(nutrient, "")
        if "," in value:
            value = value.replace(",", ".")
        result.append(
            {
                # "identification": f"{nutrient} - {chemical_property_instance.name}",
                "identification": f"{nutrient}",
                "name": f"{chemical_property_instance.name}",
                "value": float(value),
                "lower": (
                    acceptable_value.lower_value
                    if acceptable_value and hasattr(acceptable_value, "lower_value")
                    else 0
                ),
                "upper": (
                    acceptable_value.upper_value
                    if acceptable_value and hasattr(acceptable_value, "upper_value")
                    else 0
                ),
            }
        )

    return {"farmer_data": data, "result": result}


def read_csv(file_obj):
    # Get sample name from the original filename
    sample_name = file_obj.name.split("CoA_")[1].split(".csv")[0]

    # Read the file object directly using StringIO
    csv_text = file_obj.read().decode("utf-8")
    csv_file = io.StringIO(csv_text)
    csv_reader = csv.reader(csv_file)

    # Initialize data structure
    data = {"metadata": {}, "samples": []}

    rows = list(csv_reader)  # Convert to list for easier processing

    # Process header section (metadata)
    for row in rows:
        if "Parameter" in row:
            parameter_index = row.index(
                "Parameter"
            )  # Get the index of the "Parameter" column
            header_row_index = rows.index(row)
            break

        if len(row) >= 5:  # Ensure row has enough columns
            key = row[0].strip(": ")
            values = row[4:]  # Get all sample values starting from column 5

            # print(f"Processing key: {key}, values: {values}")

            if key == "Client Sample ID":
                data["samples"] = [{"sample_id": id} for id in values if id]
            elif key in [
                "Crop ID",
                "Sample Date",
                "Sampled By",
                "Sample Depth",
                "Your Client",
                "EAL Sample ID",
            ]:
                # Store in metadata and also distribute to each sample
                data["metadata"][key] = values[0]  # Store first value in metadata
                for i, sample in enumerate(data["samples"]):
                    sample[key] = values[i] if i < len(values) else values[0]

    
    # print('\nn\n data["samples"]')
    # print(data["samples"])
    # Black Tank Hills Clay Pit

    # Define nutrients to skip
    SKIP_NUTRIENTS = {"Crude Protein", "Carbon / Nitrogen Ratio", "Total Carbon"}

    # Process parameter data
    parameters_start = header_row_index + 1
    for row in rows[parameters_start:]:
        if len(row) >= 5:  # Ensure row has enough columns
            parameter = row[parameter_index]

            # Skip specified nutrients
            if parameter in SKIP_NUTRIENTS:
                continue

            unit = row[1]
            method = row[2]
            lor = row[3]
            values = row[4:]

            # Add parameter data to each sample
            for i, sample in enumerate(data["samples"]):
                if "parameters" not in sample:
                    sample["parameters"] = []

                if i < len(values):
                    value = values[i]
                    # Handle less than values
                    if value.startswith("< "):
                        value = value.replace("< ", "<")

                    sample["parameters"].append(
                        {
                            "parameter": parameter,
                            "unit": unit,
                            "method": method,
                            "LOR": lor,
                            "value": value,
                        }
                    )

    return data


def calculate_tae_data(method_data, crop_instance):
    nutrient_mapping = {
        "Phosphorus": {
            "name": "Phosphorus",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Calcium": {
            "name": "Calcium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Magnesium": {
            "name": "Magnesium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Potassium": {
            "name": "Potassium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Sodium": {
            "name": "Sodium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Sulfur": {
            "name": "Sulfur",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3120 ICPOES",
        },
        "Aluminium": {
            "name": "Aluminium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Silicon": {
            "name": "Silicon",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Boron": {
            "name": "Boron",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Iron": {
            "name": "Iron",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Manganese": {
            "name": "Manganese",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Copper": {
            "name": "Copper",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Zinc": {
            "name": "Zinc",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Molybdenum": {
            "name": "Molybdenum",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Cobalt": {
            "name": "Cobalt",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
        "Selenium": {
            "name": "Selenium",
            "unit": "mg/kg",
            "method": "1:3 Nitric:HCl - APHA 3125 ICPMS",
        },
    }
    result = []
    updated_method_data = []
    acceptable_value = None

    for row in method_data:
        parameter_name = row["parameter"]
        if (
            parameter_name in nutrient_mapping
            and row["unit"] in [info["unit"] for info in nutrient_mapping.values()]
            and row["method"] in [info["method"] for info in nutrient_mapping.values()]
        ):
            row["parameter"] = nutrient_mapping.get(parameter_name, {}).get("name")
            row["unit"] = nutrient_mapping.get(parameter_name, {}).get("unit")
            updated_method_data.append(row)
    for tae_row in updated_method_data:
        chemical_property_instance = ChemicalProperty.objects.filter(
            name=tae_row["parameter"]
        ).first()
        
        symbol = (
            f"{chemical_property_instance.symbol}" if chemical_property_instance else ""
        )
        
        acceptable_value = TaeAcceptableValues.objects.filter(
            crop=crop_instance, chemical_property=chemical_property_instance
        ).first()
        
        # Get the original value and handle special characters
        original_value = tae_row["value"]
        icon = ""
        numeric_value = original_value

        # Check for special characters like '<' and extract numeric value
        if isinstance(original_value, str):
            original_value = original_value.strip()
            if original_value.startswith('<'):
                icon = '<'
                numeric_value = original_value[1:].strip()
            elif original_value.startswith('>'):
                icon = '>'
                numeric_value = original_value[1:].strip()
            else:
                numeric_value = original_value

            # Replace comma with dot for decimal values
            numeric_value = numeric_value.replace(',', '.')
            
            try:
                numeric_value = float(numeric_value)
            except ValueError:
                numeric_value = 0

        # Update the original row's value with the numeric value for calculations
        tae_row["value"] = numeric_value
        
        result.append({
            "identification": symbol,
            "name": (
                chemical_property_instance.name
                if chemical_property_instance
                else f"{symbol}{tae_row['parameter']}"
            ),
            "value": numeric_value,  # Numeric value for calculations
            "display_value": f"{icon}{numeric_value}" if icon else str(numeric_value),  # For display
            "icon": icon,
            "lower": (
                acceptable_value.lower_value
                if acceptable_value and hasattr(acceptable_value, "lower_value")
                else 0
            ),
            "upper": (
                acceptable_value.upper_value
                if acceptable_value and hasattr(acceptable_value, "upper_value")
                else 0
            ),
        })
    return result


def calculate_lamotte_data(method_data, crop_instance):
    result = []
    nutrient_mapping = {
        "Soluble Calcium": {"name": "Calcium", "unit": "mg/kg", "method": "** Inhouse S10 - Morgan"},
        "Soluble Magnesium": {"name": "Magnesium", "unit": "mg/kg", "method": "** Inhouse S10 - Morgan"},
        "Soluble Phosphorus": {"name": "Phosphorus", "unit": "mg/kg", "method": "** Inhouse S10 - Morgan"},
        "Soluble Potassium": {"name": "Potassium", "unit": "mg/kg", "method": "** Inhouse S10 - Morgan"},
        # "Soluble Sodium - ESP":{"name": "Sodium", "unit":}
    }
    updated_method_data = []
    acceptable_value = None

    for row in method_data:
        parameter_name = row["parameter"]
        if parameter_name in nutrient_mapping and row["unit"] in [
            info["unit"] for info in nutrient_mapping.values()
        ] and row["method"] in [info["method"] for info in nutrient_mapping.values()]:
            row["parameter"] = nutrient_mapping.get(parameter_name, {}).get("name")
            row["unit"] = nutrient_mapping.get(parameter_name, {}).get("unit")
            updated_method_data.append(row)
    method_data = updated_method_data

    for row in method_data:
        chemical_property_instance = ChemicalProperty.objects.filter(
            name=row["parameter"]
        ).first()
        symbol = (
            f"{chemical_property_instance.symbol}" if chemical_property_instance else ""
        )
        acceptable_value = LamotteAcceptableValues.objects.filter(
            crop=crop_instance, chemical_property=chemical_property_instance
        ).first()

        # Handle special value formats like '<1'
        value = row["value"]
        icon = ""
        numeric_value = value

        # Check for special characters and extract numeric value
        if isinstance(value, str):
            value = value.strip()
            if value.startswith('<'):
                icon = '<'
                numeric_value = value[1:].strip()
            elif value.startswith('>'):
                icon = '>'
                numeric_value = value[1:].strip()
            
            # Replace comma with dot for decimal values
            numeric_value = numeric_value.replace(',', '.')
            
            try:
                numeric_value = float(numeric_value)
            except ValueError:
                numeric_value = 0

        result.append({
            "identification": chemical_property_instance.symbol if chemical_property_instance else "",
            "name": row["parameter"] if chemical_property_instance else row['parameter'],
            "value": numeric_value,  # Store numeric value for calculations
            "display_value": f"{icon}{numeric_value}" if icon else str(numeric_value),  # For display
            "icon": icon,  # Store the icon separately
            "lower": (
                acceptable_value.lower_value
                if acceptable_value and hasattr(acceptable_value, "lower_value")
                else 0
            ),
            "upper": (
                acceptable_value.upper_value
                if acceptable_value and hasattr(acceptable_value, "upper_value")
                else 0
            ),
        })

    return result


def calculate_csv_data(method_data, crop_instance, analysis_type="plant"):
    result = []
    nutrient_mapping = {
        # Add Nitrogen mapping explicitly for plant analysis
        "Nitrogen": {"name": "Nitrogen", "unit": "%", "method": "**Inhouse S37"},
        "N": {"name": "Nitrogen", "unit": "%", "method": "**Inhouse S37"},
        "Total Nitrogen": {"name": "Nitrogen", "unit": "%", "method": "**Inhouse S37"},
        "Total N": {"name": "Nitrogen", "unit": "%", "method": "**Inhouse S37"},
        "Paramagnetism": {"name": "Paramagnetism", "unit": "µCGS", "method": "** Paramagnetic Count Soil Meter"},
        "pH (H2O)": {"name": "pH-level", "unit": "units", "method": "Rayment & Lyons 2011 - 4A1"},
        "Estimated Organic Matter": {"name": "Organic Matter", "unit": "%", "method": "Inhouse S4a"},
        "Carbon - Total": {"name": "Organic Carbon", "unit": "%", "method": "Inhouse S4a"},
        "Electrical Conductivity": {"name": "Conductivity", "unit": "dS/m", "method": "Rayment & Lyons 2011 - 3A1"},
        "Nitrate-N - KCl extractable": {"name": "Nitrate-N", "unit": "mg/kg", "method": "** Inhouse S37"},
        "Ammonium-N - KCl extractable": {"name": "Ammonium-N", "unit": "mg/kg", "method": "** Inhouse S37"},
        "Mehlich Phosphorus": {"name": "Phosphorus", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 18F1 (Mehlich 3)"},

        "Phosphorus - Colwell": {"name": "Phosphorus - Colwell", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 9B2"},
        "Phosphorus Buffer Index": {"name": "Phosphorus Buffer Index", "unit": "---", "method": "** Rayment & Lyons 2011 - 9I2b"},
        "Phosphorus - acid extractable": {"name": "Phosphorus - acid extractable", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 9G2"},

        "Exchangeable Calcium": {"name": "Calcium", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 18F1 (Mehlich 3)"},
        "Exchangeable Magnesium": {"name": "Magnesium", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 18F1 (Mehlich 3)"},
        "Exchangeable Potassium": {"name": "Potassium", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 18F1 (Mehlich 3)"},
        "Exchangeable Sodium": {"name": "Sodium", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 18F1 (Mehlich 3)"},
        "Sulfur - KCl extractable": {
            "name": "Sulfur",
            "unit": "mg/kg",
            "method": "** Inhouse S37"
        },
        "Hydrogen": {"name": "Hydrogen", "unit": "%", "method": "** Calculation"},
        # "Total Sulfur": {
        #     "name": "Sulfur",
        #     "unit": ["mg/kg", "%"],  # Accept both units
        #     "method": "**Inhouse S37"
        # },
        # "Total S": {
        #     "name": "Sulfur",
        #     "unit": ["mg/kg", "%"],
        #     "method": "**Inhouse S37"
        # },
        # "Sulfur": {
        #     "name": "Sulfur",
        #     "unit": ["%", "mg/kg"],  # Accept both units
        #     "method": ["1:3 Nitric:HCl - APHA 3120 ICPOES", "**Inhouse S37"]  # Accept both methods
        # },
        # "Sulphur": {
        #     "name": "Sulfur",
        #     "unit": ["%", "mg/kg"],
        #     "method": ["1:3 Nitric:HCl - APHA 3120 ICPOES", "**Inhouse S37"]
        # },
        "Maximum Soil Chloride Estimate": {"name": "Chloride", "unit": "mg/kg", "method": "** Calculation (Electrical Conductivity x 640)"},
        "Aluminium - Exchangeable": {"name": "Aluminium", "unit": "mg/kg", "method": ["** Inhouse S37", "** Calculations"]},
        "Silicon - CaCl2 extractable": {"name": "Silicon", "unit": "mg/kg", "method": "** Inhouse S11"},
        "Boron - CaCl2 extractable": {"name": "Boron", "unit": "mg/kg", "method": "** Rayment & Lyons 2011 - 12C2"},
        "Iron - DTPA": {
            "name": "Iron",
            "unit": "mg/kg",
            "method": "Rayment & Lyons 2011 - 12A1"
        },
        "Manganese - DTPA": {
            "name": "Manganese",
            "unit": "mg/kg",
            "method": "Rayment & Lyons 2011 - 12A1"
        },
        "Copper - DTPA": {
            "name": "Copper",
            "unit": "mg/kg",
            "method": "Rayment & Lyons 2011 - 12A1"
        },
        "Zinc - DTPA": {
            "name": "Zinc",
            "unit": "mg/kg",
            "method": "Rayment & Lyons 2011 - 12A1"
        },
        "Basic Texture": {"name": "Texture", "unit": "---", "method": "** Inhouse S65"},
        "Basic Colour": {"name": "Colour", "unit": "---", "method": "** Inhouse S65"},
        # "Silicon": {
        #     "name": "Silicon",
        #     "unit": "mg/kg",
        #     "method": ["1:3 Nitric:HCl - APHA 3125 ICPMS"]  # Accept both methods
        # },
        # "Silicon - CaCl2 extractable": {
        #     "name": "Silicon - CaCl2 extractable",
        #     "unit": "mg/kg",
        #     "method": ["** Inhouse S11"]  # Accept both methods
        # },
    }

    if analysis_type == "soil":
        updated_method_data = []
        for row_data in method_data:
            parameter = row_data.get("parameter")
            if not parameter:
                raise ValueError("Missing 'parameter' field in method data row.")

            if parameter in nutrient_mapping:
                mapping = nutrient_mapping[parameter]
                # Check if unit matches (handle both single unit and list of units)
                units = mapping["unit"] if isinstance(mapping["unit"], list) else [mapping["unit"]]
                methods = mapping["method"] if isinstance(mapping["method"], list) else [mapping["method"]]
                
                if (row_data["unit"] in units and 
                    row_data["method"] in methods):  # Check if method is in allowed methods
                    try:
                        updated_method_data.append({
                            "parameter": mapping["name"],
                            "unit": row_data["unit"],
                            "method": row_data["method"],
                            "LOR": row_data["LOR"],
                            "value": row_data["value"],
                        })
                    except KeyError as e:
                        raise ValueError(f"Missing required key in row data: {e}")

        method_data = updated_method_data

    # remove any row that has "sample washed" or "leaf washed" in the parameter name
    # they were causing issues in some files and we don't need the in the final report
    method_data = [
        item for item in method_data
        if not (
            'sample washed' in item['parameter'].lower()
            or 'leaf washed' in item['parameter'].lower()
        )
    ]

    for row in method_data:
        parameter_name = row.get("parameter")
        if not parameter_name:
            raise ValueError("Missing 'parameter' in method_data row.")

        # Nitrogen and Sulfur mapping logic
        if parameter_name in ["Total Nitrogen", "Total N", "Nitrogen", "N"]:
            parameter_name = "Nitrogen"
            # print(f"Mapped to Nitrogen")
        elif parameter_name in ["Total Sulfur", "Total S", "Sulfur", "Sulphur"]:
            parameter_name = "Sulfur"
            # print(f"Mapped to Sulfur")
        
        # Get chemical property
        chemical_property_instance = ChemicalProperty.objects.filter(
            name=parameter_name
        ).first()

        # if not chemical_property_instance:
        #     raise Http404(f"Chemical property '{parameter_name}' not found.")
        
        acceptable_value = None

        try:
            if analysis_type == "plant":
                acceptable_value = CropAcceptabelValues.objects.filter(
                    crop=crop_instance, chemical_property=chemical_property_instance
                ).first()
                if not acceptable_value:
                    acceptable_value = CropAcceptabelValues.objects.filter(
                        crop__name=crop_instance.name, chemical_property__name=chemical_property_instance.name
                    ).first()
            elif analysis_type == "soil":
                acceptable_value = SoilAcceptableValues.objects.filter(
                    crop=crop_instance, chemical_property=chemical_property_instance
                ).first()
        except Exception as e:
            raise Http404("Acceptable value query failed due to missing crop or chemical property.")

        value = row["value"]
        if "," in value:
            value = value.replace(",", ".")

        try:
            value = float(value)
        except:
            value = value

        result.append(
            {
                "identification": chemical_property_instance.symbol if chemical_property_instance else "",
                "name": parameter_name if chemical_property_instance else row['parameter'],
                "value": value,
                "lower": (
                    acceptable_value.lower_value
                    if acceptable_value and hasattr(acceptable_value, "lower_value")
                    else 0
                ),
                "upper": (
                    acceptable_value.upper_value
                    if acceptable_value and hasattr(acceptable_value, "upper_value")
                    else 0
                ),
            }
        )

    return result