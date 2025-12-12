from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Booking
from datetime import date, timedelta

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False, label="Номер телефона")
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('phone_number', 'email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['email'].help_text = 'Обязательное поле.'

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields

class BookingForm(forms.ModelForm):
    check_in_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
        label="Дата заезда"
    )
    check_out_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': (date.today() + timedelta(days=1)).isoformat()}),
        label="Дата выезда"
    )
    
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'guests']
        labels = {
            'guests': 'Количество гостей',
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')
        
        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise forms.ValidationError("Дата выезда должна быть позже даты заезда.")
        
        return cleaned_data
