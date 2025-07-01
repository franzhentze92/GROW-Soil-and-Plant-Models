from analysis_submissions.models import ReportSubmission
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import Q

def update_report(report_id, new_data):
    """
    Update an existing report submission with new data.

    Args:
        report_id (str): The ID of the report to update.
        new_data (dict): Dictionary of fields to update. Valid keys:
            'user_id', 'user_email', 'analysis_type', 'report_data'

    Example:
        ```
            from analysis_submissions.utils import update_report  # wherever you place the function

            updated_report = update_report(
                report_id='531cb47d897f4545',
                new_data={
                    'user_email': 'updated@email.com',
                    'analysis_type': 'plant',
                    'report_data': {'status': 'updated', 'value': 42}
                }
            )
            print(updated_report.report_data)
        ```

    
    Returns:
        ReportSubmission: The updated report instance.
    Raises:
        ReportSubmission.DoesNotExist: If report with report_id doesn't exist.
    """
    try:
        report = ReportSubmission.objects.get(report_id=report_id)
        
        if 'user_id' in new_data:
            report.user_id = new_data['user_id']
        if 'user_email' in new_data:
            report.user_email = new_data['user_email']
        if 'analysis_type' in new_data:
            report.analysis_type = new_data['analysis_type']
        if 'report_data' in new_data:
            report.report_data = new_data['report_data']
        
        report.save()
        return report
    except ReportSubmission.DoesNotExist:
        raise ReportSubmission.DoesNotExist(f"Report with ID {report_id} does not exist.")

def save_report(user_id, user_email, user_role, analysis_type, report_object, report_id=None):
    """
    Save a report submission to the database.
    Args:
        user_id (int): The ID of the user submitting the report.
        user_email (str): The email of the user submitting the report.
        report_object (dict): The report data to save.
        analysis_type (str): The type of analysis for the report.
        user_role (str): The role of the user submitting the report.
        report_id (str, optional): The ID of the report. If not provided, a new ID will be generated.
    
    """
    if report_id is None:
        submission = ReportSubmission.objects.create(
            user_id=user_id,
            user_email=user_email,
            user_role= user_role or "user",
            analysis_type=analysis_type,
            report_data=report_object
        )
    else:
        # Update existing report
        submission = ReportSubmission.objects.get(report_id=report_id)
        submission.user_id = user_id
        submission.user_email = user_email
        submission.user_role = user_role or "user"
        submission.analysis_type = analysis_type
        submission.report_data = report_object
        submission.save()

    return submission.report_id

def get_report_by_id(report_id):
    """
    Retrieve a report submission from the database.
    Args:
        report_id (str): The ID of the report to retrieve.
    
    Returns:
        ReportSubmission: The retrieved report submission object.
    """
    try:
        report = ReportSubmission.objects.get(report_id=report_id)
        return model_to_dict(report)
    except ReportSubmission.DoesNotExist:
        raise ReportSubmission.DoesNotExist(f"Report with ID {report_id} does not exist.")

# def get_reports_by_partial_id(partial_id, analysis_type, user_role):
#     """
#     Retrieve all report submissions from the database that contain the given partial ID.
    
#     Args:
#         partial_id (str): The partial ID to search for.
#         analysis_type (str): The type of analysis to filter by.
#         user_role (str): The role of the user to filter by.
    
#     Returns:
#         QuerySet: A queryset of matching ReportSubmission objects.
#     """
#     return ReportSubmission.objects.filter(
#         report_id__icontains=partial_id,
#         analysis_type=analysis_type,
#         user_role=user_role).order_by('created_at').values('user_id', 'user_email', 'user_role', 'report_id', 'analysis_type', 'report_data', 'created_at')

def get_reports_by_partial_id(search_term, analysis_type, user_role):
    """
    Retrieve report submissions matching the partial search term in either
    report_id, farm, or paddock (supports partial match in nested JSON).
    
    Args:
        search_term (str): Partial string to match in report_id, farm, or paddock.
        analysis_type (str): The type of analysis to filter by.
        user_role (str): The role of the user to filter by.
    
    Returns:
        list: Filtered list of matching report dicts.
    """
    # Initial query: filter by role, type, and possibly report_id
    qs = ReportSubmission.objects.filter(
        Q(report_id__icontains=search_term) |
        Q(report_data__sample_paddock_farm_assignments__isnull=False),
        analysis_type=analysis_type,
        user_role=user_role
    ).order_by('created_at').values(
        'user_id', 'user_email', 'user_role', 'report_id', 'analysis_type', 'report_data', 'created_at'
    )

    # Post-filter by farm/paddock with partial match
    results = []

    for report in qs:

        # Always include if report_id matches
        if search_term.lower() in report['report_id'].lower():
            results.append(report)
            continue

        # Otherwise check nested sample_paddock_farm_assignments
        assignments = report.get('report_data', {}).get('sample_paddock_farm_assignments', [])
        
        for a in assignments:
            farm = a.get('farm', '').lower() if isinstance(a.get('farm'), str) else ''
            paddock = a.get('paddock', '').lower() if isinstance(a.get('paddock'), str) else ''

            if search_term.lower() in farm or search_term.lower() in paddock:
                results.append(report)
                break  # Include each report only once

    return results

def get_report_by_user_details(user_email, user_id, analysis_type, user_role):
    """
    Retrieve all report submissions for a given user email and id.
    Args:
        user_email (str): The email of the user whose reports to retrieve.
        user_id (int): The ID of the user whose reports to retrieve.
        analysis_type (str): The type of analysis to filter by.
        user_role (str): The role of the user to filter by.

    Returns:
        QuerySet: A queryset of ReportSubmission objects.
    """
    return ReportSubmission.objects.filter(
        user_email=user_email, 
        user_id=user_id,
        analysis_type=analysis_type,
        user_role=user_role).order_by('created_at').values('user_id', 'user_email', 'user_role', 'report_id', 'analysis_type', 'report_data', 'created_at')

def get_all_reports(analysis_type, user_role):
    """
    Retrieve all report submissions from the database.
    
    Args:
        analysis_type (str): The type of analysis to filter by.
        user_role (str): The role of the user to filter by.
    
    Returns:
        QuerySet: A queryset of ReportSubmission objects.
    """
    return ReportSubmission.objects.filter(
        analysis_type=analysis_type,
        user_role=user_role).order_by('created_at').values('user_id', 'user_email', 'user_role', 'report_id', 'analysis_type', 'report_data', 'created_at')

def delete_report_by_id(report_id):
    """
    Delete a report submission from the database.
    
    Args:
        report_id (str): The ID of the report to delete.
    
    Returns:
        bool: True if the report was deleted, False otherwise.
    """
    print(f"Attempting to delete report with ID: {report_id}")  # Debug line
    try:
        report = ReportSubmission.objects.get(report_id=report_id)
        report.delete()
        return True
    except ReportSubmission.DoesNotExist:
        return False
