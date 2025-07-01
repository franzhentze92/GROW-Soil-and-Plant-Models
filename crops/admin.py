from django.contrib import admin
from .models import Crop, ChemicalProperty, CropAcceptabelValues, Fertilizer, CropGroup, FertilizerMixedFirst, FertilizerMixedSecond, LabType, InputSample


class CropAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class ChemicalPropertyAdmin(admin.ModelAdmin):
    search_fields = ("name", "symbol")


class CropAcceptableValuesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "crop",
        "chemical_property",
        "lower_value",
        "upper_value",
        "created_at",
    )
    list_filter = ("crop", "chemical_property", "created_at")
    search_fields = ("crop__name", "chemical_property__name")


class FertilizerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "chemical_property",
        "min_dose",
        "max_dose",
        "created_at",
    )
    search_fields = ("name", "chemical_property__name")


class FertilizerMixedFirstAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "chemical_property",
        "min_dose",
        "max_dose",
        "created_at",
    )
    search_fields = ("name", "chemical_property__name")

class FertilizerMixedSecondAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "chemical_property",
        "min_dose",
        "max_dose",
        "created_at",
    )
    search_fields = ("name", "chemical_property__name")


admin.site.register(CropGroup)
admin.site.register(Crop, CropAdmin)
admin.site.register(ChemicalProperty, ChemicalPropertyAdmin)
admin.site.register(CropAcceptabelValues, CropAcceptableValuesAdmin)
admin.site.register(Fertilizer, FertilizerAdmin)
admin.site.register(FertilizerMixedFirst,FertilizerMixedFirstAdmin)
admin.site.register(FertilizerMixedSecond,FertilizerMixedSecondAdmin)
admin.site.register(LabType)
admin.site.register(InputSample)