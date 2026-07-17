from django import forms
from .models import Student, Attendance


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'course', 'duration_months']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': "Student's full name",
            }),
            'course': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': 'e.g. Web development',
            }),
            'duration_months': forms.NumberInput(attrs={
                'class': 'field-input',
                'placeholder': '6',
                'min': 1,
            }),
        }


class AttendanceForm(forms.ModelForm):
    # Render is_present as Present / Absent dropdown
    is_present = forms.TypedChoiceField(
        label='Status',
        choices=[('True', 'Present'), ('False', 'Absent')],
        coerce=lambda v: v == 'True' if isinstance(v, str) else bool(v),
        widget=forms.Select(attrs={'class': 'field-select'}),
    )

    class Meta:
        model = Attendance
        fields = ['student', 'date', 'mode', 'login_time', 'logout_time', 'is_present']
        widgets = {
            'student': forms.Select(attrs={'class': 'field-select'}),
            'date': forms.DateInput(attrs={'class': 'field-input', 'type': 'date'}),
            'mode': forms.Select(attrs={'class': 'field-select'}),
            'login_time': forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
            'logout_time': forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        login_time = cleaned_data.get('login_time')
        logout_time = cleaned_data.get('logout_time')
        if login_time and logout_time and login_time >= logout_time:
            raise forms.ValidationError("Logout time must be after login time.")
        return cleaned_data
