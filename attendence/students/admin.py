from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'duration_months', 'joined_date')
    list_filter = ('course', 'joined_date')
    search_fields = ('name', 'course')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'mode', 'login_time', 'logout_time', 'is_present')
    list_filter = ('date', 'mode', 'is_present')
    search_fields = ('student__name', 'mode')
