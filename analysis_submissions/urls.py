from django.urls import path
from .views import index, get_user_reports, search_reports_by_id, delete_user_report_by_id , edit_user_report

urlpatterns = [
    path('', index, name='index'),
    path('get_user_reports/', get_user_reports, name='get_user_reports'),
    path('search_reports_by_id/', search_reports_by_id, name='search_reports_by_id'),
    path('delete_report_by_id/', delete_user_report_by_id, name='delete_user_report_by_id'),
    path('<str:report_id>/', edit_user_report, name='edit_user_report'),  # leave this last
]

