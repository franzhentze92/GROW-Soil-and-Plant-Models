from django.shortcuts import render, redirect
from common.views import validate_token
from django.http import JsonResponse
import json

# Create your views here.

@validate_token
def index(request):
    # Get the query parameters
    role = request.GET.get('role')
    analysis_type = request.GET.get('type')
    token = request.GET.get('token')

    # Set defaults if invalid
    valid_roles = ['user', 'agronomist']
    valid_types = ['soil', 'plant']

    if role not in valid_roles:
        role = 'agronomist'
    
    if analysis_type not in valid_types:
        analysis_type = 'soil'

    # If role or type in query string is missing/invalid, redirect with corrected values
    if request.GET.get('role') != role or request.GET.get('type') != analysis_type:
        return redirect(f"{request.path}?type={analysis_type}&role={role}&token={token}")

    return render(
        request,
        "analysis_analytics/index.html",
        {
            "role": role,
            "analysis_type": analysis_type,
        }
    )
