from django.contrib import admin
from .models import Student, Attendance, Batch

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display  = ('name', 'course', 'duration_hours', 'duration_days', 'created_at')
    search_fields = ('name', 'course')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'course', 'duration_hours', 'duration_days', 'batch', 'joined_date')
    list_filter   = ('course', 'joined_date', 'batch')
    search_fields = ('name', 'course')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display  = ('student', 'date', 'mode', 'login_time', 'logout_time', 'status')
    list_filter   = ('date', 'mode', 'status')
    search_fields = ('student__name', 'mode')
