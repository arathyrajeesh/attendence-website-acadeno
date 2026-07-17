from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=150)
    course = models.CharField(max_length=150)
    duration_months = models.PositiveIntegerField(help_text="Course duration in months")
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    STATUS_CHOICES = [
        ('present',  'Present'),
        ('absent',   'Absent'),
        ('no_class', 'No Class'),
    ]

    student    = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date       = models.DateField()
    mode       = models.CharField(max_length=10, choices=MODE_CHOICES)
    login_time  = models.TimeField(null=True, blank=True)
    logout_time = models.TimeField(null=True, blank=True)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date}"

    @property
    def is_present(self):
        """Backward-compatible helper."""
        return self.status == 'present'

