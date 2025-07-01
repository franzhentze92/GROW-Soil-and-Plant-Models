from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from xhtml2pdf import pisa
import json
import io
import pandas as pd
import os
from common.views import validate_token

from crops.models import CropGroup, LabType, Crop
from crops.helper import calculate_final_values_formula
from crops.utils import process_crop_data, upload_pdf_file_to_s3, read_csv, calculate_csv_data
from reporting.crop_calculators.cost_calculator import PRODUCT_PRICES, CONVERSION_FACTORS, AREA_CONVERSION_FACTORS, calculate_total_cost_all_products
from reporting.crop_calculators.units_to_kg_ha import convert_to_kg_ha
from reporting.crop_calculators.nutrient_breakdown import calculate_combined_nutrient_breakdown, calculate_nutrient_breakdown

from analysis_submissions.utils import save_report, get_report_by_id

DENSITIES_FILE_PATH = './reporting/crop_calculators/Product_Densities.xlsx' 

@validate_token
def index(request):
    crop_groups = CropGroup.objects.all().order_by('name')
    plant_lab_types = LabType.objects.filter(sample_type="plant").order_by('name')

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
        'reporting/index.html',
        {
            "crop_groups": crop_groups,
            "plant_lab_types": plant_lab_types,
            "product_ids": ['fertigation', 'foliar'], # 'foliar-spray'
            "role": role,
        })

@csrf_exempt
def get_crops_by_group(request):
    if request.method == "GET":
        group_id = request.GET.get("group_id")
        if group_id:
            crops = Crop.objects.filter(crop_group_id=group_id).values("id", "name").order_by('name')
            return JsonResponse(list(crops), safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def generate_table(request):
    crop_groups = CropGroup.objects.all().order_by('name')

    if request.method == "POST":
        try:
            if "fileInput" not in request.FILES:
                return JsonResponse({"error": "No file uploaded."}, status=400)

            file = request.FILES["fileInput"]
            crop_id = request.POST.get("crop")
            crop_group_id = request.POST.get("crop_group")
            lab_type_id = request.POST.get("lab_type")

            if not (crop_id and crop_group_id and lab_type_id):
                return JsonResponse({"error": "Missing crop, crop group, or lab type."}, status=400)

            try:
                lab_type = LabType.objects.get(id=lab_type_id)
            except LabType.DoesNotExist:
                return JsonResponse({"error": "Invalid lab type."}, status=400)

            if lab_type.name == "University of San Carlos":
                allowed_image_types = ['image/jpeg', 'image/png', 'image/jpg']
                if file.content_type not in allowed_image_types:
                    return JsonResponse({"error": "Invalid file type. Upload JPEG, PNG, or JPG."}, status=400)

                result_data = process_crop_data(file, crop_id)
                farmer_data = result_data["farmer_data"]
                calculated_crop_data = calculate_final_values_formula(result_data["result"])
                crop_data = {farmer_data["LAND_USE"]: calculated_crop_data}
                user_data = {
                    "name": farmer_data["NAME"],
                    "address": farmer_data["ADDRESS"],
                    "date": farmer_data["SAMPLE_REC"],
                    "land": farmer_data["LAND_USE"],
                }

            elif lab_type.name == "Environmental Analysis Laboratory (EAL) - Leaf":
                if not file.name.endswith('.csv'):
                    return JsonResponse({"error": "Invalid file type. Upload a CSV file."}, status=400)

                result_data = read_csv(file)
                user_data_meta = result_data["metadata"]
                method_data = result_data["samples"]
                crop_data = {}
                crop_instance = Crop.objects.get(id=crop_id)

                for val in method_data:
                    calc = calculate_csv_data(val.get('parameters', []), crop_instance)
                    crop_data[val.get('sample_id', '')] = calculate_final_values_formula(calc)

                user_data = {
                    "name": user_data_meta.get("Your Client", ""),
                    "address": "",
                    "date": user_data_meta.get("Sample Date", ""),
                    "land": user_data_meta.get("Crop ID", ""),
                }
            else:
                return JsonResponse({"error": "Invalid lab type selected."}, status=400)

            return JsonResponse({
                "success": "Data processed successfully.",
                "crop_data": crop_data,
                "user_data": user_data,
                "crop_group_id": crop_group_id
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)

@csrf_exempt
def get_products(request):
    if request.method == "GET":
        return JsonResponse({
            "product_prices": PRODUCT_PRICES, 
            "conversion_factors": CONVERSION_FACTORS, 
            "area_conversion_factors": AREA_CONVERSION_FACTORS})

@csrf_exempt
def calculate_products_cost(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            selected_products = data.get('selected_products')
            area = data.get('area')
            area_unit = data.get('area_unit')

            if not selected_products or not area or not area_unit:
                return JsonResponse({"error": "Missing required fields (selected_products, area, area_unit)."}, status=400)

            total_cost, cost_breakdown = calculate_total_cost_all_products(selected_products, area, area_unit)

            # Load densities
            products_densities = pd.read_excel(DENSITIES_FILE_PATH, sheet_name=None)['Product_density']
            products_densities.columns = products_densities.columns.str.strip()

            # Add density to products
            products_with_densities = {}
            for product_name, details in selected_products.items():
                density_row = products_densities.loc[
                    products_densities['Product'].str.strip().str.lower() == product_name.lower(),
                    'Density (g/cm³)'
                ]
                density_value = float(density_row.iloc[0]) if not density_row.empty and pd.notna(density_row.iloc[0]) else 1
                products_with_densities[product_name] = {
                    "size": details["size"],
                    "rate": details["rate"],
                    "unit": details["unit"],
                    "density": density_value,
                    "area": area
                }

            # Standardize and calculate breakdown
            products_standardized = {}
            products_breakdown = {}
            for name, d in products_with_densities.items():
                converted_rate = convert_to_kg_ha(d["rate"], d["unit"], d["density"], d["area"])
                products_standardized[name] = {"size": d["size"], "rate": converted_rate, "unit": "kg/Ha"}
                products_breakdown[name] = calculate_nutrient_breakdown(name, converted_rate)

            simplified_products = {name: d["rate"] for name, d in products_standardized.items()}
            nutrient_breakdown_combined = calculate_combined_nutrient_breakdown(simplified_products)

            return JsonResponse({
                "success": "Product cost and nutrients calculated successfully.",
                "total_cost": total_cost,
                "cost_breakdown": cost_breakdown,
                "nutrient_breakdown_combined": nutrient_breakdown_combined,
                "nutrient_breakdown_product": products_breakdown
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)


@csrf_exempt
def save_plant_agronomist_report_analysis(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            report = data.get('report')
            role = data.get('role')
            report_id = data.get('report_id', None)

            if not report:
                return JsonResponse({'error': 'Missing report.'}, status=400)

            authenticated_user = report.get('authenticated_user', {})
            if not authenticated_user:
                return JsonResponse({'error': 'Authenticated user not found in the report.'}, status=400)

            del report['authenticated_user']

            report_id = save_report(
                user_id=authenticated_user.get('id'),
                user_email=authenticated_user.get('email'),
                user_role=role,
                analysis_type="plant_report",
                report_object=report,
                report_id=report_id
            )

            return JsonResponse({'success': 'Report saved successfully.', 'id': report_id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method.'}, status=405)
