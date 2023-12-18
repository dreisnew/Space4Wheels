# forms.py

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['reservation_start_date', 'reservation_end_date', 'status']
        widgets = {
            'reservation_start_date': forms.DateInput(attrs={'type': 'date'}),
            'reservation_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the labels for non-editable fields
        self.fields['status'].label = "Status"

        # Make the fields read-only
        self.fields['status'].disabled = True

    def set_initial_values(self, post, renter, host):
        self.initial['post'] = post
        self.initial['renter'] = renter
        self.initial['host'] = host
        self.initial['status'] = 'pending'


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Search'}))


