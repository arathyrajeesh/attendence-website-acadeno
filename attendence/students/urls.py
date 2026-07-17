from django.urls import path
from . import views

urlpatterns = [
    # Student URLs — add form is embedded on the list page
    path('', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('students/<int:pk>/export/pdf/', views.export_student_pdf, name='student-export-pdf'),
    path('students/<int:pk>/export/excel/', views.export_student_excel, name='student-export-excel'),

    # Attendance URLs — mark-attendance form is embedded on the list page
    path('attendance/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance-update'),
    path('attendance/<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance-delete'),
]