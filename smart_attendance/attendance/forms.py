# attendance/forms.py

from django import forms
from .models import Topic
from .models import AttendanceEntry
import re


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title']

class AttendanceEntryForm(forms.ModelForm):
    class Meta:
        model = AttendanceEntry
        fields = ['name', 'roll_number','selfie']
        widgets = {
            'selfie': forms.HiddenInput(),
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Check if the name contains only letters (allowing spaces for multiple names)
        if not re.match(r'^[A-Za-z ]+$', name):
            raise forms.ValidationError("Please enter characters only.")
        return name

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        # Check if the roll number contains only digits and has exactly 10 digits
        if not roll_number.isdigit():
            raise forms.ValidationError("Please enter numbers only.")
        if len(roll_number) != 10:
            raise forms.ValidationError("Please enter a 10-digit roll number.")
        return roll_number
