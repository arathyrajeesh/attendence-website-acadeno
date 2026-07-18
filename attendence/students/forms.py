from django import forms
from .models import Student, Attendance, Batch


class StudentForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields = ['name', 'course', 'duration_hours', 'duration_days', 'batch']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': "Student's full name",
            }),
            'course': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': 'e.g. Web development',
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'field-input',
                'placeholder': '100',
                'min': 0,
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'field-input',
                'placeholder': '15',
                'min': 0,
            }),
            'batch': forms.Select(attrs={'class': 'field-select'}),
        }
        labels = {
            'duration_hours': 'Duration (hours)',
            'duration_days':  'Duration (days)',
            'batch':          'Batch / Group (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].required = False
        self.fields['batch'].empty_label = '— No batch —'


class BatchForm(forms.ModelForm):
    """Form to create a batch/group of students."""
    # Textarea for pasting student names — one per line
    student_names = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'field-input',
            'rows': 6,
            'placeholder': 'Paste student names, one per line:\nAlice Johnson\nBob Smith\nCarol White',
            'style': 'resize: vertical; font-family: monospace; font-size: 13px;',
        }),
        label='Student Names',
        help_text='One name per line. Students will all share the course and duration below.',
    )

    class Meta:
        model  = Batch
        fields = ['name', 'course', 'duration_hours', 'duration_days']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': 'e.g. ABC Engineering College — Batch 2024',
            }),
            'course': forms.TextInput(attrs={
                'class': 'field-input',
                'placeholder': 'e.g. Full-Stack Web Development',
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'field-input',
                'placeholder': '100',
                'min': 0,
            }),
            'duration_days': forms.NumberInput(attrs={
                'class': 'field-input',
                'placeholder': '15',
                'min': 0,
            }),
        }
        labels = {
            'name':           'Batch / College Name',
            'duration_hours': 'Total Hours',
            'duration_days':  'Total Days',
        }

    def clean(self):
        cleaned = super().clean()
        raw = cleaned.get('student_names', '')
        names = [n.strip() for n in raw.splitlines() if n.strip()]
        if not names:
            raise forms.ValidationError("Please enter at least one student name.")
        cleaned['parsed_names'] = names
        hours = cleaned.get('duration_hours', 0)
        days  = cleaned.get('duration_days', 0)
        if not hours and not days:
            raise forms.ValidationError("Please specify at least hours or days for the duration.")
        return cleaned


class AttendanceForm(forms.ModelForm):
    class Meta:
        model  = Attendance
        fields = ['student', 'date', 'mode', 'login_time', 'logout_time', 'status']
        widgets = {
            'student':     forms.Select(attrs={'class': 'field-select'}),
            'date':        forms.DateInput(attrs={'class': 'field-input', 'type': 'date'}),
            'mode':        forms.Select(attrs={'class': 'field-select'}),
            'login_time':  forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
            'logout_time': forms.TimeInput(attrs={'class': 'field-input', 'type': 'time'}),
            'status':      forms.Select(attrs={'class': 'field-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status       = cleaned_data.get('status')
        login_time   = cleaned_data.get('login_time')
        logout_time  = cleaned_data.get('logout_time')
        date         = cleaned_data.get('date')

        if date and date.weekday() == 6:
            raise forms.ValidationError("Sunday has no class.")

        if status == 'present':
            if login_time and logout_time and login_time >= logout_time:
                raise forms.ValidationError("Logout time must be after login time.")
        else:
            cleaned_data['login_time']  = None
            cleaned_data['logout_time'] = None

        return cleaned_data
