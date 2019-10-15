from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
    # desirability_rank = forms.IntegerField(
    #     validators=[MinValueValidator(1), MaxValueValidator(5)],
    #     widget=forms.NumberInput(attrs={'class': 'form-control'}),
    #     required=False
    #     # help_text="Input value from 1 (least desirable) to 5 (most desirable)"
    # )
    active_til = forms.DateField(
        # help_text="Provide a date if you want your gift wish to expire after a particular time",
        widget=forms.DateInput(attrs={'class': 'form-control'})
    )


class MarkGiftFilled(forms.Form):
    filled = forms.BooleanField(
        required=False
    )

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    # last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2', )

class InviteFriend(forms.Form):
    email = forms.EmailField(
        max_length=254,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label="Message",
        max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False)