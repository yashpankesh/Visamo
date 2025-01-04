from django import forms
from django.contrib.auth.models import User
from .models import Booking
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number' , 'password1', 'password2']


class BookingForm(forms.ModelForm):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Check-in Date",
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Check-out Date",
    )

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'rooms_booked']

