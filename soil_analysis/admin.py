from django.contrib import admin
from .models import SoilSample, BaseSaturationAcceptableValues, SoilAcceptableValues, LamotteAcceptableValues, TaeAcceptableValues, ConversionFactor, BaseSaturationHighTecValues

class BaseSaturationAcceptableValuesAdmin(admin.ModelAdmin):
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

class SoilAcceptableValuesAdmin(admin.ModelAdmin):
    list_display = ("id", "crop", "chemical_property", "lower_value", "upper_value", "created_at")
    list_filter = ("crop", "chemical_property", "created_at")
    search_fields = ("crop__name", "chemical_property__name")

class LamotteAcceptableValuesAdmin(admin.ModelAdmin):
    list_display = ("id", "crop", "chemical_property", "lower_value", "upper_value", "created_at")
    list_filter = ("crop", "chemical_property", "created_at")
    search_fields = ("crop__name", "chemical_property__name")

class TaeAcceptableValuesAdmin(admin.ModelAdmin):
    list_display = ("id", "crop", "chemical_property", "lower_value", "upper_value", "created_at")
    list_filter = ("crop", "chemical_property", "created_at")
    search_fields = ("crop__name", "chemical_property__name")

@admin.register(ConversionFactor)
class ConversionFactorAdmin(admin.ModelAdmin):
    list_display = ('id','crop','chemical_property','nutrient', 'factor', 'updated_at')
    search_fields = ('nutrient',)
    ordering = ('nutrient',)

class BaseSaturationHighTecValuesAdmin(admin.ModelAdmin):
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

admin.site.register(SoilSample)
admin.site.register(BaseSaturationAcceptableValues, BaseSaturationAcceptableValuesAdmin)
admin.site.register(SoilAcceptableValues, SoilAcceptableValuesAdmin)
admin.site.register(LamotteAcceptableValues, LamotteAcceptableValuesAdmin)
admin.site.register(TaeAcceptableValues, TaeAcceptableValuesAdmin)
admin.site.register(BaseSaturationHighTecValues, BaseSaturationHighTecValuesAdmin)