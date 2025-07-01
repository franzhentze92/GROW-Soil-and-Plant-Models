from crops.models import Crop
from crops.utils import textract_client, s3, s3_bucket, extract_table_data
import boto3
import json
import time
import pandas as pd

def load_soil_recommendation_xlsx(filpath):
    """Load the soil recommendation data from an Excel file."""
    explanation_df = pd.read_excel(filpath, sheet_name="Soil Nutrient Explanation")
    return explanation_df

def get_nutrient_explanation_from_df(df, category, nutrient, status):
    """Extract the nutrient explanation data from a DataFrame."""

    # Strip whitespace from relevant columns
    df['Category'] = df['Category'].str.strip()
    df['Nutrient'] = df['Nutrient'].str.strip()
    df['Status'] = df['Status'].str.strip()

    filtered = df.loc[
        (df['Category'] == category) &
        (df['Nutrient'] == nutrient) &
        (df['Status'] == status)
    ]['Explanation'].values
    
    if len(filtered) == 0:
        # return f"No explanation available for {nutrient}."
        return ""
    
    return filtered[0]

def process_textract_response(response_data):
    """Process Textract response into readable format"""
    blocks = response_data.get("Blocks", [])

    # Initialize data structures
    tables = []
    key_value_pairs = {}
    lines = []

    # Process each block
    for block in blocks:
        block_type = block.get("BlockType", "")

        if block_type == "TABLE":
            # Process table data
            table_cells = []
            for rel in block.get("Relationships", []):
                if rel.get("Type") == "CHILD":
                    row = []
                    for cell_id in rel.get("Ids", []):
                        cell = next((b for b in blocks if b["Id"] == cell_id), None)
                        if cell:
                            row.append(cell.get("Text", ""))
                    if row:
                        table_cells.append(row)
            tables.append(table_cells)

        elif block_type == "KEY_VALUE_SET":
            # Process key-value pairs
            if block.get("EntityTypes", []) == ["KEY"]:
                key = block.get("Text", "")
                for rel in block.get("Relationships", []):
                    if rel["Type"] == "VALUE":
                        for v_id in rel["Ids"]:
                            value = next((b for b in blocks if b["Id"] == v_id), None)
                            if value:
                                key_value_pairs[key] = value.get("Text", "")

        elif block_type == "LINE":
            # Collect all text lines
            lines.append(block.get("Text", ""))

    return {"tables": tables, "key_value_pairs": key_value_pairs, "lines": lines}


def structure_data_by_sample_location(extracted_lines):
    # Dictionary to store structured data
    structured_data = {}

    current_sample_location = None
    current_data = []

    for line in extracted_lines:
        # Check for "Sample Location" format
        if "Sample Location" in line and not line.startswith("SAMPLE LOCATION"):
            # If there's a current sample location, save its data
            if current_sample_location:
                structured_data[current_sample_location] = current_data

            # Set the new sample location and reset current data
            idx = extracted_lines.index(line)
            current_sample_location = extracted_lines[idx + 1]
            current_data = []

        # Check for "SAMPLE LOCATION" format
        elif "SAMPLE LOCATION:" in line:
            # If there's a current sample location, save its data
            if current_sample_location:
                structured_data[current_sample_location] = current_data

            # Extract sample location identifier from the line
            current_sample_location = line.split(":")[-1].strip()
            current_data = []

        # Add lines to current sample location's data
        elif current_sample_location:
            current_data.append(line)

    # Add the last sample location data to the dictionary
    if current_sample_location:
        structured_data[current_sample_location] = current_data

    return structured_data


def analyze_document(file):
    """
    Analyzes a PDF document using AWS Textract and returns the extracted data.

    Args:
        file: The uploaded PDF file from a Flask form.

    Returns:
        dict: The response from Textract containing the extracted data.
    """
    # Define the S3 key for the uploaded file
    s3_key = f"temp/{file.name}"  # Adjust attribute as needed (e.g., file.filename)

    # Upload the file to S3
    file.seek(0)  # Go to the start of the file if previously read elsewhere
    s3.upload_fileobj(file, s3_bucket, s3_key)

    response = textract_client.analyze_document(
        Document={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
        FeatureTypes=["TABLES"])

    # Start document analysis
    # try:
    #     response = textract_client.start_document_analysis(
    #         DocumentLocation={"S3Object": {"Bucket": s3_bucket, "Name": s3_key}},
    #         FeatureTypes=["TABLES"],
    #     )
    # except textract_client.exceptions.BadDocumentException:
    #     raise ValueError("The uploaded document appears to be empty or invalid")

    # Get the JobId from the response
    # job_id = response["JobId"]

    # Wait for the analysis to complete
    # while True:
    #     response = textract_client.get_document_analysis(JobId=job_id)

    #     # Check for job completion
    #     if response["JobStatus"] in ["SUCCEEDED", "FAILED"]:
    #         break
    #     time.sleep(5)  # Wait before checking the job status again

    return response


# def analyze_document(pdf_file):
#     # Convert Django InMemoryUploadedFile to bytes for Textract
#     pdf_bytes = pdf_file.read()

#     # Call AWS Textract to analyze the document
#     response = textract_client.analyze_document(
#         Document={'Bytes': pdf_bytes},
#         FeatureTypes=['TABLES', 'FORMS']
#     )

#     # Optionally, you can process the response here or in a separate function
#     return response

def get_table_data(job_id):
    all_tables = []
    next_token = None

    while True:
        # Get document analysis response
        if next_token:
            response = textract_client.get_document_analysis(
                JobId=job_id, NextToken=next_token
            )
        else:
            response = textract_client.get_document_analysis(JobId=job_id)

        # Extract tables from response
        tables = extract_tables_from_response(response)
        all_tables.extend(tables)

        # Check for NextToken
        next_token = response.get("NextToken")
        if not next_token:
            break

    return all_tables


def extract_tables_from_response(response):
    tables = []
    blocks = response.get("Blocks", [])

    for block in blocks:
        if block["BlockType"] == "TABLE":
            # Extract table data from the Table block
            table_data = extract_table(block, blocks)
            tables.append(table_data)

    return tables


def extract_table(table_block, blocks):
    # Map of cell ID to cell information
    cell_map = {block["Id"]: block for block in blocks if block["BlockType"] == "CELL"}

    table_data = []
    for relationship in table_block.get("Relationships", []):
        if relationship["Type"] == "CHILD":
            for cell_id in relationship["Ids"]:
                cell = cell_map.get(cell_id)
                if cell:
                    # Extract text for this cell
                    cell_text = extract_text_from_cell(cell, blocks)
                    row = cell.get("RowIndex", 0)
                    col = cell.get("ColumnIndex", 0)

                    # Ensure the table has enough rows
                    while len(table_data) < row:
                        table_data.append([])

                    # Ensure the current row has enough columns
                    while len(table_data[row - 1]) < col:
                        table_data[row - 1].append("")

                    # Add cell text to the table
                    table_data[row - 1][col - 1] = cell_text

    return table_data


def extract_text_from_cell(cell, blocks):
    # Map of word ID to text
    text_map = {
        block["Id"]: block["Text"] for block in blocks if block["BlockType"] == "WORD"
    }

    cell_text = []
    for relationship in cell.get("Relationships", []):
        if relationship["Type"] == "CHILD":
            for word_id in relationship["Ids"]:
                text = text_map.get(word_id)
                if text:
                    cell_text.append(text)

    return " ".join(cell_text)


def parse_key_value_pairs(response):
    blocks = response['Blocks']
    key_map = {}
    value_map = {}
    block_map = {}
    
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    key_value_pairs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map) if value_block else None
        key_value_pairs[key] = val
    
    return key_value_pairs

def find_value_block(key_block, value_map):
    for relationship in key_block.get('Relationships', []):
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                if value_id in value_map:
                    return value_map[value_id]
    return None

def get_text(result, block_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child = block_map[child_id]
                    if child['BlockType'] == 'WORD':
                        text += child['Text'] + ' '
                    elif child['BlockType'] == 'SELECTION_ELEMENT':
                        if child['SelectionStatus'] == 'SELECTED':
                            text += 'X '
    return text.strip()



def extract_key_value_pairs_by_page(blocks):
    # Organize blocks by page
    pages = {}
    for block in blocks:
        page_number = block.get('Page', None)
        if page_number:
            if page_number not in pages:
                pages[page_number] = []
            pages[page_number].append(block)
    
    # Process each page to extract key-value pairs
    page_data = {}
    for page_number, blocks in pages.items():
        key_map = {}
        value_map = {}
        block_map = {}

        # Classify and map blocks
        for block in blocks:
            block_id = block['Id']
            block_map[block_id] = block
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block['EntityTypes']:
                    key_map[block_id] = block
                elif 'VALUE' in block['EntityTypes']:
                    value_map[block_id] = block

        # Extract key-value pairs
        key_value_pairs = {}
        for key_id, key_block in key_map.items():
            value_block = find_value_block(key_block, value_map, block_map)
            key_text = get_text(key_block, block_map)
            value_text = get_text(value_block, block_map) if value_block else 'N/A'
            key_value_pairs[key_text] = value_text
        
        page_data[page_number] = key_value_pairs
    
    return page_data

def find_value_block(key_block, value_map, block_map):
    for relationship in key_block.get('Relationships', []):
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                if value_id in value_map:
                    return value_map[value_id]
    return None

def get_text(block, block_map):
    text = ''
    if 'Relationships' in block:
        for relationship in block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child_block = block_map[child_id]
                    if child_block['BlockType'] == 'WORD':
                        text += child_block['Text'] + ' '
    return text.strip()

def process_textract_response(response_data):
    """Process the Textract response to extract tables, key-value pairs, and lines of text."""
    blocks = response_data.get("Blocks", [])
    tables = []
    key_value_pairs = {}
    lines = []

    for block in blocks:
        block_type = block.get("BlockType", "")

        if block_type == "TABLE":
            table_cells = []
            for rel in block.get("Relationships", []):
                if rel.get("Type") == "CHILD":
                    row = []
                    for cell_id in rel.get("Ids", []):
                        cell = next((b for b in blocks if b["Id"] == cell_id), None)
                        if cell:
                            row.append(cell.get("Text", ""))
                    if row:
                        table_cells.append(row)
            tables.append(table_cells)

        elif block_type == "KEY_VALUE_SET":
            if "KEY" in block.get("EntityTypes", []):
                key = block.get("Text", "")
                for rel in block.get("Relationships", []):
                    if rel["Type"] == "VALUE":
                        for v_id in rel["Ids"]:
                            value = next((b for b in blocks if b["Id"] == v_id), None)
                            if value:
                                key_value_pairs[key] = value.get("Text", "")

        elif block_type == "LINE":
            lines.append(block.get("Text", ""))

    return {"tables": tables, "key_value_pairs": key_value_pairs, "lines": lines}

def save_data_to_json(data, output_file):
    """Save the extracted data to a JSON file."""
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        