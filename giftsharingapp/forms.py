from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class CreateGiftForm(forms.Form):
    name = forms.CharField(
        label="Gift Name",
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Gift Description",
        max_length=2000,
        # help_text="Describe your desired gift",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
    )
    link = forms.URLField(
        max_length=2000,
        label="Link to the gift",
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        required=False
        )
    price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    desirability_rank = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    active_til = forms.DateField(
        # help_text="Provide a date if you want your gift wish to expire after a particular time",
        widget=forms.DateInput(attrs={'class': 'form-control'})
    )


class MarkGiftFilled(forms.Form):
    filled = forms.BooleanField(
        required=False
    )


