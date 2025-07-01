from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import pandas as pd
from crops.helper import calculate_final_values_formula
from crops.models import ChemicalProperty, LabType, Crop
from soil_analysis.models import SoilAcceptableValues, BaseSaturationAcceptableValues
from soil_analysis.helper import calculate_base_saturation, get_ratio, tec_matrix
from crops.utils import read_csv, calculate_csv_data, calculate_lamotte_data, calculate_tae_data
from copy import deepcopy
from django.http import JsonResponse
from soil_analysis.utils import load_soil_recommendation_xlsx, get_nutrient_explanation_from_df
import os
import json
from common.views import validate_token
from django.core.exceptions import ObjectDoesNotExist
import traceback

from analysis_submissions.utils import save_report, get_report_by_id

RECOMMENDATION_FOLDER_PATH = './soil_analysis/recommendation/' 
SOIL_RECOMMENDATION_FILE = os.path.join(RECOMMENDATION_FOLDER_PATH, "Soil Nutrient Explanations.xlsx")

def process_excel_file(df, crop_id):
    # Print column headers and first few rows to see the structure
    print("\nExcel Sheet Structure:")
    print("Columns:", df.columns.tolist())
    print("\nFirst few rows of data:")
    print(df.head())

    # Function to process a single Excel file and return sample results and lab data
    lab_header = df.columns[0]
    lab_name = lab_header.split(",")[0].strip()
    address_start = lab_header.find("Inc.") + 4
    address_end = lab_header.find("(")
    lab_address = lab_header[address_start:address_end].strip()
    
    print("\nLab Information:")
    print(f"Lab Header: {lab_header}")
    print(f"Lab Name: {lab_name}")
    print(f"Lab Address: {lab_address}")

    lab_data = {
        "name": lab_name or "",
        "address": lab_address or "",
        "client_number": df.iloc[0, 1] if pd.notna(df.iloc[0, 1]) else "",
        "date_submitted": df.iloc[1, 1] if pd.notna(df.iloc[1, 1]) else "",
        "date_received": df.iloc[2, 1] if pd.notna(df.iloc[2, 1]) else "",
        "date_reported": df.iloc[3, 1] if pd.notna(df.iloc[3, 1]) else "",
    }

    sample_data = {}
    for _, row in df.iloc[6:].iterrows():
        # Get column headers from row 6 as keys
        column_headers = df.iloc[6].values

        # Get the sample location and description
        sample_location = row[df.columns[0]].strip()
        sample_description = row[df.columns[1]].strip() if len(df.columns) > 1 else ""

        if sample_location and sample_location != "Sample Location":
            # Create a composite key using both location and description
            composite_key = f"{sample_location}_{sample_description}" if sample_description else sample_location
            
            # Create dictionary for this sample
            sample_data[composite_key] = {
                "location": sample_location,
                "description": sample_description
            }

            # Map each column value to its header
            for col_idx, header in enumerate(column_headers):
                if pd.notna(header):  # Only include non-null headers
                    value = row[df.columns[col_idx]]
                    # Convert to string if not null, otherwise use empty string
                    value = str(value) if pd.notna(value) else ""
                    if header != "Sample Location" and header != "Sample Description #1":
                        sample_data[composite_key][header] = value.strip()

    sample_results = {}
    key_name = (
        "selenium" if "selenium" in df.columns.str.lower() else "analysis_data"
    )  # Determine key name

    for composite_key, data in sample_data.items():
        sample_results[composite_key] = []
        print(f"\nProcessing Sample: {composite_key}")
        for nutrient, value in data.items():
            if nutrient not in ["location", "description", "Lab Number"]:
                print(f"  Nutrient: {nutrient}, Raw Value: {value}")
                try:
                    # Skip base saturation percentage nutrients but not Boron
                    if any(x in nutrient for x in [
                        "Ca** (%)", "Mg** (%)", "K** (%)", "Na** (%)",
                        "Other Bases** (%)", "H** (%)", "Al** (%)"
                    ]):
                        continue

                    clean_nutrient = nutrient.split("*")[0].strip()
                    if "(" in clean_nutrient:
                        clean_nutrient = clean_nutrient.split("(")[0].strip()

                    if clean_nutrient == "Molybdenum- M3":
                        clean_nutrient = "Mo"
                    elif clean_nutrient == "Cobalt- M3":
                        clean_nutrient = "Co"

                    print(f"    Cleaned Nutrient: {clean_nutrient}")
                    
                    chemical_property_instance = ChemicalProperty.objects.filter(
                        symbol=clean_nutrient
                    ).first()
                    
                    if chemical_property_instance:
                        print(f"    Found Chemical Property: {chemical_property_instance.symbol} - {chemical_property_instance.name}")
                        acceptable_value = SoilAcceptableValues.objects.filter(
                            crop_id=crop_id,
                            chemical_property=chemical_property_instance,
                        ).first()

                        upper_value = (
                            acceptable_value.upper_value
                            if acceptable_value and hasattr(acceptable_value, "upper_value")
                            else 0
                        )
                        
                        lower_value = (
                            acceptable_value.lower_value
                            if acceptable_value and hasattr(acceptable_value, "lower_value")
                            else 0
                        )
                        
                        print(f"    Processed Values - Upper: {upper_value}, Lower: {lower_value}")
                        
                        # Handle special value formats like '<0.05'
                        icon = ""
                        numeric_value = value
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
                            float_value = float(numeric_value)
                        except ValueError:
                            float_value = 0
                            
                        sample_results[composite_key].append({
                            "identification": chemical_property_instance.symbol,
                            "name": chemical_property_instance.name,
                            # "value": float_value,  # Numeric value for calculations
                            "value": f"{icon}{numeric_value}" if icon else str(numeric_value),  # Original format for display
                            "icon": icon,  # Store the icon separately
                            "lower": lower_value,
                            "upper": upper_value,
                        })
                        print(f"    Added to results with value: {float_value} (display: {icon}{numeric_value})")
                except (ValueError, AttributeError) as e:
                    print(f"    Error processing nutrient {nutrient}: {e}")
                    continue

    print("\nFinal Sample Results:")
    for location, results in sample_results.items():
        print(f"\nLocation: {location}")
        for result in results:
            print(f"  {result['name']}: {result['value']} (Range: {result['lower']} - {result['upper']})")

    return lab_data, sample_results


def get_sample_results_from_xls(xls_files, crop_id):
    lab_data_list = []
    sample_results_combined = {}
    for xls_file in xls_files:
        df = pd.read_excel(xls_file)
        lab_data, sample_results = process_excel_file(df, crop_id)
        # print("lab_data ---->> ",lab_data)
        lab_data_list.append(lab_data)
        # print(sample_results,"--------------00000000000000000000000000000")
        # Combine sample results into the new dictionary
        for sample_location, results in sample_results.items():
            if sample_location not in sample_results_combined:
                sample_results_combined[sample_location] = []
            sample_results_combined[sample_location].extend(results)
    return lab_data_list, sample_results_combined

def extract_ppm_values(result):
    """ Extract PPM values from the result list. """
    ppm_values = {
        "Ca": 0, "Mg": 0, "K": 0, "Na": 0, "H": 0, "OB": 0, 
        "P": 0, "S": 0, "Zn": 0, "Fe": 0, "Mn": 0, "Al": 0, "pH": 0,
        "Mo": 0, "Co": 0  # Added Molybdenum and Cobalt
    }
    
    # List of nutrients that should be set to 0 if they have '<' prefix
    zero_if_less_than = ["Ca", "Mg", "K", "Na", "H", "pH"]
    
    for nutrient in result:
        identification = nutrient["identification"]

        # if identification.startswith("Molybdenum"):
        #     identification = "Mo"
        # elif identification.startswith("Cobalt"):
        #     identification = "Co"

        value = str(nutrient["value"])
        
        if identification in ppm_values:
            # Check if value has '<' prefix and nutrient is in special list
            if identification in zero_if_less_than and value.startswith('<'):
                ppm_values[identification] = 0
            else:
                # Clean and convert the value
                clean_value = value.replace('<', '').replace('>', '').strip()
                try:
                    ppm_values[identification] = float(clean_value)
                except ValueError:
                    ppm_values[identification] = 0
        
                    
    return ppm_values

def safe_divide(numerator, denominator):
    try:
        # Convert both values to float
        num = float(str(numerator).replace('<', '').replace('>', '').strip())
        den = float(str(denominator).replace('<', '').replace('>', '').strip())
        return round(num / den, 2) if den != 0 else 0
    except (ValueError, TypeError):
        return 0

#     return ratios
def calculate_ideal_ratios(ppm_values, base_sat, meq_values, tec):
    """ Calculate the ideal nutrient ratios. """
    ratios = []

    # Helper function to safely calculate ratios
    def safe_divide(numerator, denominator):
        if denominator == 0:
            return 0  # or return None, or some other value indicating undefined
        return round(numerator / denominator, 2)

    ratios.append({
        "name": "P/S Ratio",
        "value": safe_divide(ppm_values["P"], ppm_values["S"]),
        "lower": 0.8,
        "ideal": 1.0,
        "deficient": safe_divide(0.8, 1.5),
        "excessive": safe_divide(1.0 * 1.5, 1)
    })

    ratios.append({
        "name": "P/Zn Ratio",
        "value": safe_divide(ppm_values["P"], ppm_values["Zn"]),
        "lower": 8,
        "ideal": 10.0,
        "deficient": safe_divide(8, 1.5),
        "excessive": safe_divide(10.0 * 1.5, 1)
    })

    ratios.append({
        "name": "Fe/Mn Ratio",
        "value": safe_divide(ppm_values["Fe"], ppm_values["Mn"]),
        "lower": 0.8,
        "ideal": 1.10,
        "deficient": safe_divide(0.8, 1.5),
        "excessive": safe_divide(1.10 * 1.5, 1)
    })

    # Calculate ca/mg with the new tec matrix condition
    ideal_ca_mg_ratio = 0
    for entry in tec_matrix:
        if entry["min"] <= tec < entry["max"]:
            ideal_ca_mg_ratio = entry["ratio"]
            break

    ratios.append({
        "name": "Ca/Mg Ratio",
        # "value": safe_divide(ppm_values["Ca"], ppm_values["Mg"]),
        "value": safe_divide(meq_values["Ca"], meq_values["Mg"]),
        "ideal": ideal_ca_mg_ratio, # round(base_sat['Ca']['upper'] / base_sat['Mg']['upper'], 2),
        "lower": 0,
        "deficient": 0,
        # "excessive": safe_divide(ppm_values["Ca"] / ppm_values["Mg"] * 1.5, 1),
        "excessive": safe_divide(meq_values["Ca"] / meq_values["Mg"] * 1.5, 1),
    })

    ratios.append({
        "name": "Mg/K Ratio",
        "value": safe_divide(ppm_values["Mg"], ppm_values["K"]),
        "ideal": 1.0,
        "lower": 0.8,
        "deficient": safe_divide(0.8, 1.5),
        "excessive": safe_divide(1.0 * 1.5, 1),
    })

    ratios.append({
        "name": "K/Na Ratio",
        "value": safe_divide(ppm_values["K"], ppm_values["Na"]),
        "lower": 3.5,
        "ideal": 5.0,
        "deficient": safe_divide(3.5, 1.5),
        "excessive": safe_divide(5.0 * 1.5, 1),
    })

    return ratios

def calculate_nutrient_values(item, tec):
    """
    Calculate lower and upper values for nutrients based on TEC using updated ideal ppm ranges.
    Uses `tec_matrix` logic for dynamic nutrient calculations based on TEC levels.
    """

    def _round_up(x):
        return round(float(x), 1)

    nutrient_id = item['identification']
    ideal_ppm_ranges = {}

    for entry in tec_matrix:
        if entry["min"] <= tec < entry["max"]:
            if tec < 4:
                ideal_ppm_ranges = {
                    "Ca": (372, 620),
                    "Mg": (64.5, 107.5),
                    "K": (78, 109),
                    "Na": (5, 14),
                    "Al": (0, 2),
                }
            else:
                ideal_ppm_ranges = {
                    "Ca": (
                        round((entry["Ca"] * 0.7515 / 100) * tec * 200),
                        round((entry["Ca"] * 1.25 / 100) * tec * 200),
                    ),
                    "Mg": (
                        round((entry["Mg"] * 0.7515 / 100) * tec * 120),
                        round((entry["Mg"] * 1.25 / 100) * tec * 120),
                    ),
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
            break

    if nutrient_id in ideal_ppm_ranges:
        lower, upper = ideal_ppm_ranges[nutrient_id]
        
        # # Ensure Ca and Mg lower bounds are not zero
        # if nutrient_id in ['Ca', 'Mg'] and lower == 0:
        #     lower = round(upper * 0.75, 2)

        if nutrient_id in ["Ca", "Mg"]:
            midpoint = round((lower + upper) / 2, 2)
            lower, upper = None, midpoint  # Set lower to None and upper to midpoint to display a single value

        item['lower'] = lower
        item['upper'] = upper

    # Round Ph to one decimal place, then display in two decimals
    if nutrient_id == "pH":
        item['value'] = f"{_round_up(item['value']):.2f}" if item['value'] else 0.00
        
    return item


def process_sample_location_results(result, crop_id):
    """ Process results for a single sample location and calculate necessary values. """
    # Step 1: Extract PPM values
    ppm_values = extract_ppm_values(result)

    # Step 2: Calculate base saturation
    base_sat, tec, cec, meq_values = calculate_base_saturation(crop_id, ppm_values)

    # Step 3: Calculate ideal ratios
    ideal_ratios = calculate_ideal_ratios(ppm_values, base_sat, meq_values, tec)
    
    # print(ideal_ratios,"=================This is ideal ratios =========================")
    # Add full names to base saturation data
    base_saturation_with_names = {}
    for nutrient, data in base_sat.items():
        full_name = {
            'Ca': 'Calcium',
            'Mg': 'Magnesium',
            'K': 'Potassium',
            'Na': 'Sodium',
            'Al': 'Aluminum',
            'H': 'Hydrogen',
            'OB': 'Other Bases'
        }.get(nutrient, nutrient)
        
        base_saturation_with_names[nutrient] = {
            **data,
            'full_name': full_name
        }

    return {
        "base_saturation": base_saturation_with_names,
        "ideal_ratio_levels": ideal_ratios,
        "cec": cec,
        "tec": tec,
        # "ph_data": ph_data,  # Added pH data to the response
    }

@csrf_exempt
@validate_token
def index(request):
    soil_crops = Crop.objects.filter(analysis_type="soil").order_by('name')
    soil_lab_types = LabType.objects.filter(sample_type="soil").order_by('name')

    # Get the 'role' query parameter from the URL handle this by checking for the query parameters
    role = request.GET.get('role')
    
    # Ensure role is valid or set to 'agronomist'
    if role not in ['user', 'agronomist']:
        role = 'agronomist'

    # If the URL doesn't already include a valid role, redirect with the role
    if request.GET.get('role') != role:
        return redirect(f"{request.path}?role={role}")

    return render(
        request,
        "soil_analysis/index.html",
        {
            "soil_crops": soil_crops,
            "soil_lab_types": soil_lab_types,
            "role": role
        },
    )

@csrf_exempt
def generate_table(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        crop_id = request.POST.get("crop")
        lab_type_id = request.POST.get("lab_type")
        xls_files = request.FILES.getlist("fileInput")

        if not crop_id or not lab_type_id:
            return JsonResponse({"error": "Crop and lab type must be specified."}, status=400)

        try:
            lab_type = LabType.objects.get(id=lab_type_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Invalid lab type selected."}, status=400)

        lamotte_data_by_sample = {}
        tae_data_by_sample = {}

        if lab_type.name == "Brookside Laboratories Inc.":
            if not xls_files or len(xls_files) < 2:
                return JsonResponse({"error": "At least two Excel files must be uploaded for Brookside soil analysis."}, status=400)

            for xls_file in xls_files:
                if not xls_file.name.endswith(('.xls', '.xlsx')):
                    return JsonResponse({"error": "Only Excel files are allowed for Brookside Lab type."}, status=400)

            lab_data_list, sample_results_combined = get_sample_results_from_xls(xls_files, crop_id)

        elif lab_type.name == "Environmental Analysis Laboratory (EAL) - Soil":
            if not xls_files or not xls_files[0].name.endswith('.csv'):
                return JsonResponse({"error": "Invalid file type. Please upload a CSV file for EAL soil analysis."}, status=400)

            result_data = read_csv(xls_files[0])
            lab_data = {
                "name": result_data["metadata"].get("Sampled By") or result_data["metadata"].get("Your Client", ""),
                "date_reported": result_data["metadata"].get("Sample Date", ""),
                "client_number": result_data["metadata"].get("Sample Number") or result_data["metadata"].get("EAL Sample ID", ""),
                "land_use": result_data["metadata"].get("Crop ID", ""),
            }

            lab_data_list = [lab_data]
            sample_results_combined = {}
            crop_instance = Crop.objects.get(id=crop_id)

            for val in result_data["samples"]:
                sample_id = val.get('sample_id', '')
                calculated_crop_data = calculate_csv_data(val.get('parameters', []), crop_instance, analysis_type="soil")

                if sample_id not in sample_results_combined:
                    sample_results_combined[sample_id] = calculated_crop_data
                else:
                    i = 1
                    new_sample_id = f"{sample_id} ({val.get('Sample Depth', i)})"
                    while new_sample_id in sample_results_combined:
                        i += 1
                        new_sample_id = f"{sample_id} ({val.get('Sample Depth', i)})"
                    sample_results_combined[new_sample_id] = calculated_crop_data

                lamotte_data_by_sample[sample_id] = calculate_lamotte_data(val.get('parameters', []), crop_instance)
                tae_data_by_sample[sample_id] = calculate_tae_data(val.get('parameters', []), crop_instance)

        else:
            return JsonResponse({"error": "Unsupported lab type selected."}, status=400)

        calculated_results = {}
        for sample_location, result in sample_results_combined.items():
            original_result = [dict(item) for item in result]
            calculated_results[sample_location] = process_sample_location_results(result, crop_id)

            tec = calculated_results[sample_location].get('tec', 0)
            for i in range(len(original_result)):
                original_result[i] = calculate_nutrient_values(original_result[i], tec)

            final_values = calculate_final_values_formula(original_result)
            calculated_results[sample_location]["final_values"] = final_values

        context = {
            "success": "Data processed successfully.",
            "lab_data": lab_data_list[0],
            "sample_data": sample_results_combined,
            "calculated_results": calculated_results,
            "lamotte_data": lamotte_data_by_sample,
            "tae_data": tae_data_by_sample,
        }

        return JsonResponse(context, status=200)

    except Exception as e:
        return JsonResponse({
            "error": "An error occurred while processing the files.",
            "details": str(e),
            "trace": traceback.format_exc()  # Optional: remove in production
        }, status=500)

@csrf_exempt
def generate_recommendations(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        # Get the values
        nutrient_deficient_raw = request.POST.get("nutrient_deficient")
        nutrient_optimal_raw = request.POST.get("nutrient_optimal")
        nutrient_excess_raw = request.POST.get("nutrient_excess")

        if not all([nutrient_deficient_raw, nutrient_optimal_raw, nutrient_excess_raw]):
            return JsonResponse({'error': 'Missing required nutrient inputs'}, status=400)
        
        # from json string to json object
        nutrient_deficient = json.loads(nutrient_deficient_raw)
        nutrient_optimal = json.loads(nutrient_optimal_raw)
        nutrient_excess = json.loads(nutrient_excess_raw)

        # prompt_context = ''
        explanations = {}  # dictionary to hold all category explanations
        response = {}

        # load the nutrients explanation file
        explanation_df = load_soil_recommendation_xlsx(SOIL_RECOMMENDATION_FILE)

        # prepare the prompt context text for the model
        for nutrient in nutrient_deficient:
            # get the nutrient explanation (probably returns a string)
            explanation = get_nutrient_explanation_from_df(
                df=explanation_df,
                category=nutrient['category'],
                nutrient=nutrient['value'].strip(),
                status="Deficient"
            )

            category = nutrient['category']
            if category in explanations:
                explanations[category] += f" {explanation}"
            else:
                explanations[category] = explanation

        # for nutrient in nutrient_optimal: ...
        for nutrient in nutrient_excess:
            # get the nutrient explanation (probably returns a string)
            explanation = get_nutrient_explanation_from_df(
                df=explanation_df,
                category=nutrient['category'],
                nutrient=nutrient['value'].strip(),
                status="Excessive"
            )

            category = nutrient['category']
            if category in explanations:
                explanations[category] += f" {explanation}"
            else:
                explanations[category] = explanation

        # --------------------------------------------------------------------------------------------------------------------
        # we need to make sure that all sections are available in the generated report
        # to do so, we can add the missing sections to the response from the optimal nutrient list
        # but first, we need to identify the missing sections
        all_sections = ["Organic Matter", "CEC", "Soil pH", "Base Saturation", "Available Nutrients", "Lamotte Reams", "TAE"]
        current_sections = explanations.keys()
        missing_sections = set(all_sections) - set(current_sections)

        # get the objects from the nutrient_optimal list that contains the same category as in the missing sections
        missing_sections_payload = []
        for section in missing_sections:
            for nutrient in nutrient_optimal:
                if section == nutrient['category']:
                    missing_sections_payload.append(nutrient)

        # adding the missing sections to the response
        for nutrient in missing_sections_payload:
            explanation = get_nutrient_explanation_from_df(
                df=explanation_df,
                category=nutrient['category'],
                nutrient=nutrient['value'].strip(),
                status="Optimal"
            )
            category = nutrient['category']
            explanations[category] = explanation

        # ------------------------------------------------------------------------------------------------------------------------
        # Adding definitions to certain nutrients
        if "Base Saturation" in explanations:
            explanations['Base Saturation'] = "The base saturation refers to the proportion of the soil's cation exchange capacity (CEC) that is occupied by basic cations. Basic cations include calcium (Ca2+), magnesium (Mg2+), potassium (K+), and sodium (Na+). The base saturation level is expressed as a percentage and represents the relative abundance of these basic cations in relation to the total CEC. " + (explanations['Base Saturation'] or "Base saturation nutrients are balanced.")

        if "Soil pH" in explanations:
            explanations['Soil pH'] = "The soil pH is driven by the base saturation distribution. " + (explanations['Soil pH'] or "Soil pH is balanced.")        

        if "Available Nutrients" in explanations:
            explanations['Available Nutrients'] = "This section presents the levels of key plant-available nutrients found in the soil at the time of sampling. These are the nutrients most readily taken up by plant roots and play a vital role in supporting healthy growth, yield, and crop quality. " + (explanations['Available Nutrients'] or "Available nutrients are balanced.")

        if "Lamotte Reams" in explanations:
            explanations['Lamotte Reams'] = "This test measures the biologically available nutrient levels in the soil, reflecting what plants can access through natural biological processes. " + (explanations['Lamotte Reams'] or "Lamotte reams nutrients are balanced.")

        if "TAE" in explanations:
            explanations['TAE'] = "This section shows the Total Acid Extractable (TAE) nutrient levels, which represent the total amount of each element present in the soil, regardless of whether it is currently available to plants. This provides insight into the overall mineral reserves in the soil, including those locked in the parent material or unavailable forms. " + (explanations['TAE'] or "TAE nutrients are balanced")

        response['success'] = 'Recommendations generated successfully.'
        response['combined_nutrients_explanation'] = explanations
        return JsonResponse(response, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format in request body or POST data'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key in data: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)


@csrf_exempt
def save_soil_analysis(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))

        report = data.get('report')
        role = data.get('role')
        report_id = data.get('report_id', None)

        if not report or not role:
            return JsonResponse({'error': 'Missing required fields: report or role'}, status=400)

        authenticated_user = report.get('authenticated_user', {})
        if not authenticated_user:
            return JsonResponse({'error': 'Missing authenticated_user information'}, status=400)

        # delete authenticated_user from the report
        del report['authenticated_user']

        # Save the report data
        report_id = save_report(
            user_id=authenticated_user.get('id'),
            user_email=authenticated_user.get('email'),
            user_role=role, 
            analysis_type="soil",
            report_object=report,
            report_id=report_id 
        )

        return JsonResponse({'id': report_id, "success": f"Report saved successfully with ID value {report_id}."}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

def tolerance_test(request):
    """View to serve the tolerance system test page"""
    return render(request, 'tolerance-test.html')