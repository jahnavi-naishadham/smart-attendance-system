# attendance/forms.py

from django import forms
from .models import Topic
from .models import AttendanceEntry

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
