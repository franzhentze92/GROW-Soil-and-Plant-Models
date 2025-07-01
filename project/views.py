from django.shortcuts import render, redirect
from crops.models import CropGroup, LabType, Crop

from common.views import validate_token

@validate_token
def index_view(request):
    # Get the 'role' query parameter from the URL handle this by checking for the query parameters
    role = request.GET.get('role')
    token = request.GET.get('token')

    # Set default role to 'agronomist' if no role is provided (matching the decorator)
    if not role:
        role = 'agronomist'

    # If the URL doesn't already include the role parameter, redirect to include it
    if 'role' not in request.GET:
        return redirect(f"{request.path}?role={role}")

    return render(
        request,
        "index.html",
        {'role': role,
         "token": token
        }
    )
