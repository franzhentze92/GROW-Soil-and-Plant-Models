from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .utils import get_report_by_user_details, get_all_reports, get_reports_by_partial_id, delete_report_by_id, get_report_by_id
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from common.views import validate_token
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

@validate_token
def index(request):
    # Get the query parameters
    role = request.GET.get('role')
    analysis_type = request.GET.get('type')
    token = request.GET.get('token')

    # Set defaults if invalid
    valid_roles = ['user', 'agronomist']
    valid_types = ['soil', 'plant', 'plant_report']

    if role not in valid_roles:
        role = 'agronomist'
    
    if analysis_type not in valid_types:
        analysis_type = 'soil'

    # If role or type in query string is missing/invalid, redirect with corrected values
    if request.GET.get('role') != role or request.GET.get('type') != analysis_type:
        return redirect(f"{request.path}?type={analysis_type}&role={role}&token={token}")

    return render(
        request,
        "analysis_submissions/index.html",
        {
            "role": role,
            "analysis_type": analysis_type,
        }
    )

@validate_token
def edit_user_report(request, report_id):
    """
    View to handle the report editing.
    """
    try:
        # Get the query parameters
        role = request.GET.get('role')
        analysis_type = request.GET.get('type')
        
        # Set defaults if invalid
        valid_roles = ['user', 'agronomist']
        valid_types = ['soil', 'plant', 'plant_report']

        if role not in valid_roles:
            role = 'agronomist'
        
        if analysis_type not in valid_types:
            analysis_type = 'soil'

        # If role or type in query string is missing/invalid, redirect with corrected values
        if request.GET.get('role') != role or request.GET.get('type') != analysis_type:
            return redirect(f"{request.path}?type={analysis_type}&role={role}")

        report = json.dumps(get_report_by_id(report_id), cls=DjangoJSONEncoder)

        data = {
            "role": role,
            "analysis_type": analysis_type,
            "report": report,
            "report_id": report_id,
        }

        if analysis_type == 'plant_report':
            data["product_ids"] = ['fertigation', 'foliar']
        
        return render(request, f'analysis_submissions/edit_{analysis_type}_submission.html',
            data
        )

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
        })

@csrf_exempt
def get_user_reports(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_email = data.get('user_email')
            user_id = data.get('user_id')
            analysis_type = data.get('analysis_type')
            user_role = data.get('user_role')
            page = data.get('page', 1)
            page_size = data.get('page_size', 999999999)

            reports_queryset = None

            if analysis_type == 'plant_report':
                reports_queryset = get_all_reports(analysis_type, user_role) # agronomist can see all plant generation reports
            else:
                reports_queryset = get_report_by_user_details(user_email, user_id, analysis_type, user_role)
            
            paginator = Paginator(reports_queryset, page_size)

            try:
                reports_page = paginator.page(page)
            except PageNotAnInteger:
                reports_page = paginator.page(1)
            except EmptyPage:
                reports_page = paginator.page(paginator.num_pages)

            return JsonResponse({
                "status": "success",
                "reports": list(reports_page),
                "total_reports": paginator.count,
                "num_pages": paginator.num_pages,
                "current_page": reports_page.number,
                "has_next": reports_page.has_next(),
                "has_previous": reports_page.has_previous(),
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e),
            })

@csrf_exempt
def search_reports_by_id(request):
    """
    View to handle the report retrieval by ID.
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            
            partial_id = data.get('partial_id')
            analysis_type = data.get('analysis_type')
            user_role = data.get('user_role')

            # Get the report by partial ID
            reports = get_reports_by_partial_id(partial_id, analysis_type, user_role)

            return JsonResponse({
                "status": "success",
                "reports": list(reports),
            })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
        })

@csrf_exempt
def delete_user_report_by_id(request):
    """
    View to handle the report deletion.
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            
            report_id = data.get('report_id')
            print(report_id)

            # Logic to delete the report by ID
            is_deleted = delete_report_by_id(report_id)

            if not is_deleted:
                return JsonResponse({
                    "status": "error",
                    "message": "Report deletion failed.",
                })
                
            return JsonResponse({
                "status": "success",
                "message": "Report deleted successfully.",
            })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
        })  