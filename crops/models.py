import os
from django.db import models


SAMPLE_TYPE_CHOICES = [
    ("soil", "Soil"),
    ("plant", "Plant"),
]


class CropGroup(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Crop Group"
        verbose_name_plural = "Crop Groups"


class Crop(models.Model):
    crop_group = models.ForeignKey(
        CropGroup, blank=True, null=True, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    analysis_type = models.CharField(max_length=100, choices=SAMPLE_TYPE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Crop"
        verbose_name_plural = "Crops"


class ChemicalProperty(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.symbol}"

    class Meta:
        verbose_name = "Chemical Property"
        verbose_name_plural = "Chemical Properties"


class CropAcceptabelValues(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    lower_value = models.FloatField()
    upper_value = models.FloatField()   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Crop Acceptable Value"
        verbose_name_plural = "Crop Acceptable Values"


class Fertilizer(models.Model):
    name = models.CharField(max_length=255)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    crop_group = models.ForeignKey(
        CropGroup, on_delete=models.CASCADE, blank=True, null=True
    )
    min_dose = models.FloatField()
    max_dose = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fertilizer"
        verbose_name_plural = "Fertilizers"


class FertilizerMixedFirst(models.Model):
    name = models.CharField(max_length=255)
    crop_group = models.ForeignKey(CropGroup, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    min_dose = models.FloatField()
    max_dose = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "FertilizerMixedFirst"
        verbose_name_plural = "FertilizerMixedFirst"


class FertilizerMixedSecond(models.Model):
    name = models.CharField(max_length=255)
    crop_group = models.ForeignKey(CropGroup, on_delete=models.CASCADE)
    chemical_property = models.ForeignKey(ChemicalProperty, on_delete=models.CASCADE)
    min_dose = models.FloatField()
    max_dose = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "FertilizerMixedSecond"
        verbose_name_plural = "FertilizerMixedSecond"


class LabType(models.Model):
    name = models.CharField(max_length=100)
    sample_type = models.CharField(max_length=5, choices=SAMPLE_TYPE_CHOICES)

    def __str__(self):
        return self.name


class InputSample(models.Model):
    sample_type = models.CharField(max_length=5, choices=SAMPLE_TYPE_CHOICES)
    crop = models.ForeignKey("Crop", on_delete=models.CASCADE)
    lab_type = models.CharField(max_length=100)
    file_input = models.FileField(upload_to="get_upload_path/")
    file_name = models.CharField(max_length=255)
    is_processed_successfully = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sample_type} sample for {self.crop}"

    def get_upload_path(instance, filename):
        return os.path.join(instance.sample_type, filename)

    file_input = models.FileField(upload_to=get_upload_path)