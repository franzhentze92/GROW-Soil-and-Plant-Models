from django import forms
from .models import SoilSample

class SoilSampleForm(forms.ModelForm):
    class Meta:
        model = SoilSample
        fields = ['crop_group', 'lab_type', 'file_input'] 