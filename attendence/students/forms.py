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
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'mode', 'login_time', 'logout_time', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'field-select'}),
            'date': forms.DateInput(attrs={'class': 'field-input', 'type': 'date'}),
            'mode': forms.Select(attrs={'class': 'field-select'}),
            'login_time': forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
            'logout_time': forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'field-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        login_time = cleaned_data.get('login_time')
        logout_time = cleaned_data.get('logout_time')
        attendance_date = cleaned_data.get('date')

        if attendance_date and attendance_date.weekday() == 6:
            raise forms.ValidationError("Sunday has no class.")

        if status == 'present':
            if login_time and logout_time and login_time >= logout_time:
                raise forms.ValidationError("Logout time must be after login time.")
        else:
            cleaned_data['login_time'] = None
            cleaned_data['logout_time'] = None

        return cleaned_data
