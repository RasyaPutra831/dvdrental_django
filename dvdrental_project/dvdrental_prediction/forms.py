from django import forms
from .models import Actor, Category, Language

class MovieSearchForm(forms.Form):
    actor = forms.ModelChoiceField(queryset=Actor.objects.all(), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

class CustomerPredictionForm(forms.Form):
    store_id = forms.IntegerField(label='Store ID', min_value=1)
    active = forms.IntegerField(label='Active (0 or 1)', min_value=0, max_value=1)
    total_payment = forms.FloatField(label='Total Payment', min_value=0)
    payment_count = forms.IntegerField(label='Payment Count', min_value=0)
    average_payment = forms.FloatField(label='Average Payment', min_value=0)