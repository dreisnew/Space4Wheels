from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'reservation_start_date': forms.DateInput(attrs={'type': 'date'}),
            'reservation_end_date': forms.DateInput(attrs={'type': 'date'}),
            'post': forms.TextInput(attrs={'readonly': 'readonly'}),
            'host': forms.TextInput(attrs={'readonly': 'readonly'}),
            'renter': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial values for non-editable fields
        self.fields['post'].disabled = True
        self.fields['host'].disabled = True
        self.fields['renter'].disabled = True

    def set_initial_values(self, post, renter, host):
        self.initial['post'] = post
        self.initial['renter'] = renter
        self.initial['host'] = host
