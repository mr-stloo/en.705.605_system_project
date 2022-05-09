from django import forms
from .models import Target

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ("name","pic1","pic2","pic3")


