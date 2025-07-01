from django.db import models
from crops.models import Crop, ChemicalProperty


class SoilSample(models.Model):
    crop_group = models.CharField(max_length=100)
    lab_type = models.CharField(max_length=100)
    file_input = models.FileField(upload_to="soil_samples/")

    def __str__(self):
        return self.crop_group


class SoilAcceptableValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Soil Acceptable Value"
        verbose_name_plural = "Soil Acceptable Values"


class BaseSaturationAcceptableValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Base Saturation Acceptable Value"
        verbose_name_plural = "Base Saturation Acceptable Values"

class BaseSaturationHighTecValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Base Saturation High TEC Value"
        verbose_name_plural = "Base Saturation High TEC Values"
        unique_together = ('crop', 'chemical_property')

    def __str__(self):
        return f"{self.crop.name} - {self.chemical_property.name} - TEC>4"

class LamotteAcceptableValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lamotte Acceptable Value"
        verbose_name_plural = "Lamotte Acceptable Values"

class TaeAcceptableValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    class Meta:
        verbose_name = "TAE Acceptable Value"
        verbose_name_plural = "TAE Acceptable Values"

class ConversionFactor(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    nutrient = models.CharField(max_length=10)
    factor = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conversion Factor"
        verbose_name_plural = "Conversion Factors"
        unique_together = ('crop', 'chemical_property', 'nutrient')

    def __str__(self):
        return f"{self.crop.name} - {self.chemical_property.name} - {self.nutrient} - {self.factor}"