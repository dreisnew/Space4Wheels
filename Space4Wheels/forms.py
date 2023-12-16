from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'reservation_start_date': forms.DateInput(attrs={'type': 'date'}),
            'reservation_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the labels for non-editable fields
        self.fields['post'].label = "Title "
        self.fields['host'].label = "Host "
        self.fields['renter'].label = "Renter "

        # Disable the fields
        self.fields['post'].disabled = True
        self.fields['host'].disabled = True
        self.fields['renter'].disabled = True
        self.fields['status'].disabled = True

    def set_initial_values(self, post, renter, host):
        self.initial['post'] = post.title 
        self.initial['renter'] = renter.username 
        self.initial['host'] = host.username 
        self.initial['status'] = 'pending'
