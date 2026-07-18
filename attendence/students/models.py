from django.db import models


class Batch(models.Model):
    """A group/cohort of students from the same institution."""
    name        = models.CharField(max_length=200, help_text="College or institution name")
    course      = models.CharField(max_length=150)
    duration_hours = models.PositiveIntegerField(default=0, help_text="Total course hours")
    duration_days  = models.PositiveIntegerField(default=0, help_text="Total course days")
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.course}"

    @property
    def duration_display(self):
        parts = []
        if self.duration_hours:
            parts.append(f"{self.duration_hours} hrs")
        if self.duration_days:
            parts.append(f"{self.duration_days} days")
        return " & ".join(parts) if parts else "—"


class Student(models.Model):
    name           = models.CharField(max_length=150)
    course         = models.CharField(max_length=150)
    duration_hours = models.PositiveIntegerField(default=0, help_text="Course duration in hours")
    duration_days  = models.PositiveIntegerField(default=0, help_text="Course duration in days")
    joined_date    = models.DateField(auto_now_add=True)
    batch          = models.ForeignKey(
        Batch, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students', help_text="Optional batch/group this student belongs to"
    )

    def __str__(self):
        return self.name

    @property
    def duration_display(self):
        parts = []
        if self.duration_hours:
            parts.append(f"{self.duration_hours} hrs")
        if self.duration_days:
            parts.append(f"{self.duration_days} days")
        return " & ".join(parts) if parts else "—"


class Attendance(models.Model):
    MODE_CHOICES = [
        ('online',  'Online'),
        ('offline', 'Offline'),
    ]
    STATUS_CHOICES = [
        ('present',  'Present'),
        ('absent',   'Absent'),
        ('no_class', 'No Class'),
    ]

    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date        = models.DateField()
    mode        = models.CharField(max_length=10, choices=MODE_CHOICES)
    login_time  = models.TimeField(null=True, blank=True)
    logout_time = models.TimeField(null=True, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date}"

    @property
    def is_present(self):
        """Backward-compatible helper."""
        return self.status == 'present'
