import json
import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from crops.models import Crop, Fertilizer, CropGroup, ChemicalProperty, FertilizerMixedFirst, FertilizerMixedSecond, LabType
from crops.helper import calculate_final_values_formula
from crops.utils import process_crop_data, upload_pdf_file_to_s3, read_csv, calculate_csv_data, load_recommendations_excel_data, get_nutrient_explanation, get_products_recommendations, generate_recommendations_summary
from django.contrib import messages
from analysis_submissions.utils import save_report, get_report_by_id
from common.views import validate_token

from crops.constants import fertiliser_matrix,REQUIRE_AT_LEAST_X_PERCENT_DEFICIENT,REQUIRE_EXACTLY_Y_PERCENT_DEFICIENT,X_PERCENT_THRESHOLD,Y_PERCENT_THRESHOLD

RECOMMENDATION_FOLDER_PATH = './crops/recommendation/' 
RECOMMENDATION_DEFICIENCIES_FILE = os.path.join(RECOMMENDATION_FOLDER_PATH, "Leaf Analysis Nutrient Deficiencies Explanation.xlsx")
RECOMMENDATION_EXCESS_FILE = os.path.join(RECOMMENDATION_FOLDER_PATH, "Leaf Recommendation Excess Explanation.xlsx")
RECOMMENDATION_PRODUCT_FILE = os.path.join(RECOMMENDATION_FOLDER_PATH, "Product Recommendation for Leaf Test.xlsx")

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
        'fertilization/analysis_report.html',
        {
            "crop_groups": crop_groups,
            "plant_lab_types": plant_lab_types,
            "role": role
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
        if "fileInput" not in request.FILES:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        try:
            file = request.FILES["fileInput"]
            crop_id = request.POST.get("crop")
            crop_group_id = request.POST.get("crop_group")
            lab_type_id = request.POST.get("lab_type")
            lab_type = LabType.objects.get(id=lab_type_id)

            if lab_type.name == "University of San Carlos":
                allowed_image_types = ['image/jpeg', 'image/png', 'image/jpg']
                if file.content_type not in allowed_image_types:
                    return JsonResponse({"error": "Invalid file type. Please upload a JPEG, PNG, or JPG image."}, status=400)

                result_data = process_crop_data(file, crop_id)
                farmer_data = result_data["farmer_data"]
                calculated_crop_data = calculate_final_values_formula(result_data["result"])
                crop_data = {
                    farmer_data["LAND_USE"]: calculated_crop_data
                }
                user_data = {
                    "name": farmer_data["NAME"],
                    "address": farmer_data["ADDRESS"],
                    "date": farmer_data["SAMPLE_REC"],
                    "land": farmer_data["LAND_USE"],
                }

            elif lab_type.name == "Environmental Analysis Laboratory (EAL) - Leaf":
                if not file.name.endswith('.csv'):
                    return JsonResponse({"error": "Invalid file type. Please upload a correct CSV file."}, status=400)

                result_data = read_csv(file)
                user_data = result_data["metadata"]
                crop_data = {}
                method_data = result_data["samples"]
                crop_instance = Crop.objects.get(id=crop_id)
                for val in method_data:
                    calculated_crop_data = calculate_csv_data(val.get('parameters', []), crop_instance)
                    calculated_crop_data = calculate_final_values_formula(calculated_crop_data)
                    crop_data[val.get('sample_id', '')] = calculated_crop_data

                user_data = {
                    "name": user_data.get("Your Client", ""),
                    "address": "",
                    "date": user_data.get("Sample Date", ""),
                    "land": user_data.get("Crop ID", ""),
                }

            else:
                return JsonResponse({"error": "Invalid lab type selected."}, status=400)

            context = {
                "crop_data": crop_data,
                "user_data": user_data,
                "crop_group_id": crop_group_id,
                "success": "Data processed successfully."
            }
            return JsonResponse(context, status=200)

        except LabType.DoesNotExist:
            return JsonResponse({"error": "Selected lab type does not exist."}, status=400)
        except Crop.DoesNotExist:
            return JsonResponse({"error": "Selected crop does not exist."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "index.html", {"crop_groups": crop_groups})

@csrf_exempt
def generate_recommendations(request):
    if request.method == "POST":
        try:
            crop_group_id = request.POST.get("leafCropGroup")
            application_method_id = request.POST.get("application_method")
            recommendation_type_id = request.POST.get("recommendation_type")
            nutrient_deficient = request.POST.get("nutrient_deficient", "").split(',')
            nutrient_excess = request.POST.get("nutrient_excess", "").split(',')

            crop_map = {
                'Broadacre Agricultural Crops': "Broadacre",
                'Hort-Field Crops & Ornamentals': "Horticulture",
                'Pasture & Forage': "Pasture ",
                'Fruit Tree, Nut Tree & Vines': "Orchards ",
            }

            application_method_map = {
                "0": "Fertigation",
                "1": "Foliar Spraying"
            }

            recommendation_type_map = {
                "0": "Conventional",
                "1": "Organic"
            }

            if crop_group_id not in crop_map:
                return JsonResponse({"error": "Invalid crop group ID."}, status=400)
            if application_method_id not in application_method_map:
                return JsonResponse({"error": "Invalid application method ID."}, status=400)
            if recommendation_type_id not in recommendation_type_map:
                return JsonResponse({"error": "Invalid recommendation type ID."}, status=400)

            crop_type = crop_map[crop_group_id]
            application_method = application_method_map[application_method_id]
            recommendation_type = recommendation_type_map[recommendation_type_id]
            prompt_context = ''
            response = {}
            products_recommendation = {"excess": [], "deficient": []}

            deficiencies_df, excesses_df, recommendations_df = load_recommendations_excel_data(
                RECOMMENDATION_DEFICIENCIES_FILE,
                RECOMMENDATION_EXCESS_FILE,
                RECOMMENDATION_PRODUCT_FILE
            )

            for nutrient in nutrient_deficient:
                if not nutrient.strip():
                    continue
                prompt_context += f"\n{nutrient} Deficiency Explanation:\n"
                prompt_context += get_nutrient_explanation(nutrient, crop_type, deficiencies_df) + "\n"
                products_recommendation['deficient'].append({
                    'nutrient': nutrient,
                    'recommended_products': get_products_recommendations(
                        nutrient, crop_type, application_method, recommendation_type, recommendations_df
                    )
                })

            for nutrient in nutrient_excess:
                if not nutrient.strip():
                    continue
                prompt_context += f"\n{nutrient} Excess Explanation:\n"
                prompt_context += get_nutrient_explanation(nutrient, crop_type, excesses_df) + "\n"
                products_recommendation['excess'].append({
                    'nutrient': nutrient,
                    'recommended_products': get_products_recommendations(
                        nutrient, crop_type, application_method, recommendation_type, recommendations_df
                    )
                })

            response['combined_nutrients_explanation'] = generate_recommendations_summary(prompt_context)
            response['products_recommendation'] = products_recommendation
            response['success'] = "Recommendations generated successfully."
            return JsonResponse(response, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)

@csrf_exempt
def fertilization(request):
    crop_groups = CropGroup.objects.all().order_by('name')  # Fetch all crop groups
    if request.method == "POST":
        if "fileInput" not in request.FILES:
            messages.error(request, "No file uploaded.")
            return redirect('index')
        
        file = request.FILES["fileInput"]
        crop_id = request.POST.get("crop")
        crop_group_id = request.POST.get("crop_group")
        lab_type_id = request.POST.get("lab_type")
        lab_type = LabType.objects.get(id=lab_type_id)
        if lab_type.name == "University of San Carlos": #University of San Carlos
            allowed_image_types = ['image/jpeg', 'image/png', 'image/jpg']
            print(allowed_image_types,"=======================")
            if file.content_type not in allowed_image_types:
                messages.error(request, "Invalid file type. Please upload a JPEG, PNG, or JPG image for plant analysis.")
                return redirect('index')
            
            result_data = process_crop_data(file, crop_id)
            farmer_data = result_data["farmer_data"]
            calculated_crop_data = calculate_final_values_formula(result_data["result"])
            crop_data = {
                farmer_data["LAND_USE"]: calculated_crop_data
            }            
            user_data = {
                "name": farmer_data["NAME"],
                "address": farmer_data["ADDRESS"],
                "date": farmer_data["SAMPLE_REC"],
                "land": farmer_data["LAND_USE"],
            }
           
        elif lab_type.name == "Environmental Analysis Laboratory (EAL) - Leaf":
            if not file.name.endswith('.csv'):
                messages.error(request, "Invalid file type. Please upload a CSV file plant analysis.")
                return redirect('index')
            result_data = read_csv(file)
            user_data = result_data["metadata"]
            crop_data = {}
            method_data = result_data["samples"]
            crop_instance = Crop.objects.get(id=crop_id)
            for val in method_data:
                calculated_crop_data = calculate_csv_data(val.get('parameters', []), crop_instance)
                calculated_crop_data = calculate_final_values_formula(calculated_crop_data)
                crop_data[val.get('sample_id', '')] = calculated_crop_data
            user_data = {
                "name": user_data.get("Your Client", ""),
                "address": "", 
                "date": user_data.get("Sample Date", ""),
                "land": user_data.get("Crop ID", ""),
            }
        else:
            messages.error(request, "Invalid lab type selected for plant analysis.")
            return redirect('index')
        # print(crop_data,"=============================")
        context = {"crop_data": crop_data, "user_data": user_data, "crop_group_id":crop_group_id}
        return render(request, "fertilization/analysis_report.html", context)
    return render(request, "index.html", {"crop_groups": crop_groups})

# View for leaf analysis
# @csrf_exempt
# def leaf_analysis(request):
#     crops = Crop.objects.all()
#     if request.method == "POST":
#         if "fileInput" not in request.FILES:
#             return JsonResponse({"error": "No image file provided"})
#         crop_id = request.POST.get("crop")
#         file = request.FILES.get("fileInput")
#         result_data = process_crop_data(file, crop_id)
#         farmer_data = result_data["farmer_data"]
#         crop_data = calculate_final_values_formula(result_data["result"])
#         user_data = {
#             "name": farmer_data["NAME"],
#             "address": farmer_data["ADDRESS"],
#             "date": farmer_data["SAMPLE_REC"],
#             "land": farmer_data["LAND_USE"],
#         }
#         context = {"crop_data": crop_data, "user_data": user_data}
#         return render(request, "pdf_template.html", context)
#     return render(request, "fertilization/leaf_analysis_form.html", {"crops": crops})


# View for uploading PDF to S3
@csrf_exempt
def upload_pdf_to_s3(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        try:
            presigned_url = upload_pdf_file_to_s3(file, file.name)
            return JsonResponse({"url": presigned_url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(
        {"error": "File not provided or HTTP method not allowed"}, status=400
    )

@csrf_exempt
def calculate_recommendation(sample_value, min_acceptable, max_acceptable, min_dose, max_dose,nutrient=None):

    # Define custom thresholds for the "big four" nutrients
    big_four_thresholds = {
        'P': {'min_divisor': 1.32, 'max_divisor': 3},
        'Ca': {'min_divisor': 1.32, 'max_divisor': 3},
        'Mg': {'min_divisor': 1.32, 'max_divisor': 3},
        'B': {'min_divisor': 1.32, 'max_divisor': 3}
    }

    # Define custom thresholds for the "big four" nutrients
    if nutrient in big_four_thresholds:
        min_divisor = big_four_thresholds[nutrient]['min_divisor']
        max_divisor = big_four_thresholds[nutrient]['max_divisor']
    else:
        min_divisor = 3
        max_divisor = 3
    
    min_threshold = ((max_acceptable - min_acceptable) / min_divisor) + min_acceptable
    max_threshold = min_threshold / max_divisor
  
    if sample_value > min_threshold:
        recommendation = 0  # No fertiliser needed
    elif sample_value <= max_threshold:
        recommendation = max_dose  # Maximum dose recommended
    else:
        proportion = (min_threshold - sample_value) / (min_threshold - max_threshold)
        recommendation = min_dose + proportion * (max_dose - min_dose)

    return recommendation

# Function to check mixed fertiliser validity based on the number of deficient nutrients needed
def check_mixed_fertiliser_validity(product_name,nutrient_name,sample_value, min_acceptable, max_acceptable, min_dose, max_dose,crop_group,fert_data,is_first_fertilizer=False):

    if not product_name:
        return False  # No fertiliser to check if product_name is NaN

    # Count the total number of nutrients in the mixed fertiliser
    total_nutrients = sum(fertiliser_matrix[product_name].values())
    deficient_count = 0

    # Calculate the number of deficient nutrients required based on the threshold
    if REQUIRE_AT_LEAST_X_PERCENT_DEFICIENT:
        required_deficiencies = max(1, int(total_nutrients * (X_PERCENT_THRESHOLD / 100)))
    elif REQUIRE_EXACTLY_Y_PERCENT_DEFICIENT:
        required_deficiencies = max(1, int(total_nutrients * (Y_PERCENT_THRESHOLD / 100)))
    else:
        required_deficiencies = total_nutrients  # Default to needing all nutrients to be deficient
        
    

    # Loop over each nutrient in the fertiliser and count deficiencies
    if product_name in fertiliser_matrix:
        for nutrient, presence in fertiliser_matrix[product_name].items():
            if presence == 1:
                
                # Check if the current row's nutrient is deficient
                if nutrient_name == nutrient and calculate_recommendation(
                    sample_value, min_acceptable, max_acceptable,
                    min_dose, max_dose,nutrient_name
                ) > 0:

                    deficient_count += 1

                elif nutrient_name != nutrient:


                    # if is_first_fertilizer:
                    fertilizer_mixed = FertilizerMixedFirst.objects.filter(chemical_property__symbol=nutrient,crop_group=crop_group).first()

                    # else:
                    #     fertilizer_mixed = FertilizerMixedSecond.objects.filter(chemical_property__symbol=nutrient,crop_group=crop_group)
                    for val in fert_data:
                        nutrient_data = val.get("nutrient")
                        value = val.get("value")
                        lower = val.get("lower")
                        upper = val.get("upper")

                        if nutrient == nutrient_data:
                            sample_value_data = value
                            min_acceptable_data = lower
                            max_acceptable_data = upper

                            if fertilizer_mixed:
                                related_recommendation = calculate_recommendation(
                                    sample_value_data,
                                    min_acceptable_data,
                                    max_acceptable_data,
                                    fertilizer_mixed.min_dose,
                                    fertilizer_mixed.max_dose,
                                    nutrient_data
                                )

                                if related_recommendation > 0:
                                    deficient_count += 1

    # Debug output to help trace the logic

    print(f"Product: {product_name}")
    print(f"Deficient Count: {deficient_count}")
    print(f"Required Deficiencies for Recommendation: {required_deficiencies}")
    
    # Evaluate based on required deficiencies
    result = deficient_count >= required_deficiencies
    print(f"Recommendation: {result}\n")
    return result


# View for Recommending Fertilizers.
@csrf_exempt
def recommend_fertilizers(request):
    if request.method == "POST":
        try:    
            print("Received POST request for recommend_fertilizers.")
            data = json.loads(request.body)
            print(f"Data received: {data}")
            mixed_data = data
            crop_group_id = data[0].get("crop_group_id")
            crop_group = CropGroup.objects.get(id=crop_group_id)
            response_list = []
            recommended_dose = None
            
            for val in data: 
                try:
                    status = val.get("status", None)
                    nutrient = val.get("nutrient")
                    # Ensure numeric values
                    value = float(val.get("value", 0))
                    lower = float(val.get("lower", 0))
                    upper = float(val.get("upper", 0))
                    
                    print(f"Processing nutrient: {nutrient}, value: {value}, lower: {lower}, upper: {upper}")
                    response_dict = {}
                    if nutrient and value is not None and lower:
                        crop_group_fertilizer = Fertilizer.objects.filter(
                            crop_group=crop_group,
                            chemical_property__symbol=nutrient
                        ).first()

                        crop_group_fertilizer_mixed_first = FertilizerMixedFirst.objects.filter(
                            crop_group=crop_group,
                            chemical_property__symbol=nutrient
                        ).first()

                        crop_group_fertilizer_mixed_second = FertilizerMixedSecond.objects.filter(
                            crop_group=crop_group,
                            chemical_property__symbol=nutrient
                        ).first()

                        if not crop_group_fertilizer:
                            print(f"No single fertilizer found for nutrient: {nutrient}")
                            continue

                        max_acceptable = upper
                        min_acceptable = lower 
                        sample_value = value
                        
                        max_dose = crop_group_fertilizer.max_dose
                        min_dose = crop_group_fertilizer.min_dose

                        recommended_dose = calculate_recommendation(sample_value, min_acceptable, max_acceptable, min_dose, max_dose, nutrient)
                        print(f"Recommended dose for {nutrient}: {recommended_dose}")

                        response_dict["single"] = {
                            "recommended_dose": round(recommended_dose, 2),
                            "nutrient": f"{crop_group_fertilizer.chemical_property.name} - {crop_group_fertilizer.chemical_property.symbol}",
                            "fertilizer": crop_group_fertilizer.name,
                        }

                        response_dict["mixed"] = {
                            "nutrient": f"{crop_group_fertilizer.chemical_property.name} - {crop_group_fertilizer.chemical_property.symbol}"
                        }

                        if crop_group_fertilizer_mixed_first:
                            max_dose_mixed_first = crop_group_fertilizer_mixed_first.max_dose
                            min_dose_mixed_first = crop_group_fertilizer_mixed_first.min_dose
                            recommended_dose_mixed_first = calculate_recommendation(sample_value, min_acceptable, max_acceptable, min_dose_mixed_first, max_dose_mixed_first, nutrient)

                            status_first = check_mixed_fertiliser_validity(crop_group_fertilizer_mixed_first.name,
                                                                    crop_group_fertilizer_mixed_first.chemical_property.symbol,
                                                                    sample_value, min_acceptable, max_acceptable, min_dose_mixed_first,
                                                                    max_dose_mixed_first, crop_group_id, mixed_data, True)

                            if status_first:
                                response_dict["mixed"]["recommended_dose_mixed_first"] = round(recommended_dose_mixed_first, 2)
                                response_dict["mixed"]["fertilizer_first"] = crop_group_fertilizer_mixed_first.name
                            else:
                                response_dict["mixed"]["recommended_dose_mixed_first"] = 0

                        if crop_group_fertilizer_mixed_second:
                            max_dose_mixed_second = crop_group_fertilizer_mixed_second.max_dose
                            min_dose_mixed_second = crop_group_fertilizer_mixed_second.min_dose
                            recommended_dose_mixed_second = calculate_recommendation(sample_value, min_acceptable, max_acceptable, min_dose_mixed_second, max_dose_mixed_second, nutrient)
                            status_second = check_mixed_fertiliser_validity(crop_group_fertilizer_mixed_second.name,
                                                                    crop_group_fertilizer_mixed_second.chemical_property.symbol,
                                                                    sample_value, min_acceptable, max_acceptable, min_dose_mixed_first,
                                                                    max_dose_mixed_first, crop_group_id, mixed_data, False)

                            if status_second:
                                response_dict["mixed"]["recommended_dose_mixed_second"] = round(recommended_dose_mixed_second, 2)
                                response_dict["mixed"]["fertilizer_second"] = crop_group_fertilizer_mixed_second.name   
                            else:
                                response_dict["mixed"]["recommended_dose_mixed_second"] = 0

                    response_list.append(response_dict)  
                    print(f"Response list updated: {response_list}")

                except (ValueError, TypeError) as e:
                    print(f"Error processing values for nutrient {val.get('nutrient')}: {e}")
                    continue

            unique_list = [json.loads(item) for item in set(json.dumps(d, sort_keys=True) for d in response_list)]
            print(f"Unique response list: {unique_list}")

            return JsonResponse({"success": True, "response": unique_list})
        except Exception as e:
            print(f"Error in recommend_fertilizers: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def save_plant_analysis(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            report = data.get('report')
            role = data.get('role')
            report_id = data.get('report_id', None)

            if not report:
                return JsonResponse({'error': 'Missing report data'}, status=400)

            if not role:
                return JsonResponse({'error': 'Missing role information'}, status=400)

            authenticated_user = report.get('authenticated_user', {})
            if not authenticated_user:
                return JsonResponse({'error': 'Authenticated user not found in the report'}, status=400)

            # Remove authenticated_user from the report to avoid saving it
            del report['authenticated_user']

            # Save the report data
            report_id = save_report(
                user_id=authenticated_user.get('id'),
                user_email=authenticated_user.get('email'),
                user_role=role,
                analysis_type="plant",
                report_object=report,
                report_id=report_id
            )

            return JsonResponse({'id': report_id, "success": f"Report saved successfully with ID value {report_id}."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)
