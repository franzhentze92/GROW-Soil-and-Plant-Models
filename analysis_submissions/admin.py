from django.contrib import admin
from .models import ReportSubmission
import json
from django.utils.safestring import mark_safe


# Register your models here.
@admin.register(ReportSubmission)
class ReportSubmissionAdmin(admin.ModelAdmin):
    list_display = ("report_id", "user_email", "user_id", "user_role", "analysis_type", "crops_type", "lab_type", "created_at", "updated_at")
    readonly_fields = ("formatted_report",)

    list_filter = ("user_email", "user_role", "analysis_type", "created_at", "updated_at")
    search_fields = ("user_email__name", "user_role__name", "analysis_type__name")

    def lab_type(self, obj):
        if obj.analysis_type == 'soil':
            return obj.report_data.get("soilLabType", "N/A") if obj.report_data else "N/A"
        elif obj.analysis_type in ['plant', "plant_report"]:
            return obj.report_data.get("plantLabType", "N/A") if obj.report_data else "N/A"

    def crops_type(self, obj):
        if obj.analysis_type == 'soil':
            return obj.report_data.get("soilCrop", "N/A") if obj.report_data else "N/A"
        elif obj.analysis_type in ['plant', "plant_report"]:
            return obj.report_data.get("leafCropGroup", "N/A") if obj.report_data else "N/A"

    def formatted_report(self, obj):
        return mark_safe(f"<pre>{json.dumps(obj.report_data, indent=2)}</pre>")

    formatted_report.short_description = "Formatted Report"
