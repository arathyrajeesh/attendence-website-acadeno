from django.urls import path
from . import views

urlpatterns = [
    # Student URLs
    path('', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/attendance/', views.StudentAttendanceDetailView.as_view(), name='student-attendance'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('students/<int:pk>/export/pdf/', views.export_student_pdf, name='student-export-pdf'),
    path('students/<int:pk>/export/excel/', views.export_student_excel, name='student-export-excel'),

    # Batch URLs
    path('batches/', views.BatchImportView.as_view(), name='batch-import'),
    path('batches/<int:pk>/', views.BatchDetailView.as_view(), name='batch-detail'),
    path('batches/<int:pk>/delete/', views.BatchDeleteView.as_view(), name='batch-delete'),
    path('batches/<int:pk>/export/pdf/', views.export_batch_pdf, name='batch-export-pdf'),
    path('batches/<int:pk>/export/excel/', views.export_batch_excel, name='batch-export-excel'),

    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance-update'),
    path('attendance/<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance-delete'),
]