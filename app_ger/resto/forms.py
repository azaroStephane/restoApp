from django import forms
from django.contrib.auth.models import User
from .models import Reservation
from time import timezone

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'num_guests']

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date < timezone.now():
            raise forms.ValidationError("La date de réservation ne peut pas être dans le passé.")
        return date

    def clean_num_guests(self):
        num_guests = self.cleaned_data.get("num_guests")
        if num_guests <= 0:
            raise forms.ValidationError("Le nombre d'invités doit être positif.")
        return num_guests