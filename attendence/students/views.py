import datetime
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin

from .models import Student, Attendance
from .forms import StudentForm, AttendanceForm


# ── Student Views ──────────────────────────────────────────────────────────────

class StudentListView(FormMixin, ListView):
    """Student list + inline add form on the same page."""
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    ordering = ['-id']
    form_class = StudentForm
    success_url = reverse_lazy('student-list')

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class StudentUpdateView(SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')
    success_message = "Student %(name)s updated successfully."


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')

    def post(self, request, *args, **kwargs):
        messages.success(request, "Student deleted successfully.")
        return super().post(request, *args, **kwargs)


# ── Attendance Views ───────────────────────────────────────────────────────────

class AttendanceListView(FormMixin, ListView):
    """Attendance records + inline mark-attendance form on the same page."""
    model = Attendance
    template_name = 'students/attendance_list.html'
    context_object_name = 'attendances'
    form_class = AttendanceForm
    success_url = reverse_lazy('attendance-list')

    def get_queryset(self):
        date_str = self.request.GET.get('date', '')
        try:
            filter_date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
        except ValueError:
            filter_date = datetime.date.today()
        return (Attendance.objects
                .select_related('student')
                .filter(date=filter_date)
                .order_by('-id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = self.request.GET.get('date', '')
        today = str(datetime.date.today())
        context['selected_date'] = date_str or today
        context['is_today'] = not date_str or date_str == today
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance marked successfully.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class AttendanceUpdateView(SuccessMessageMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'students/attendance_form.html'
    success_url = reverse_lazy('attendance-list')
    success_message = "Attendance record updated successfully."


class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'students/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance-list')

    def post(self, request, *args, **kwargs):
        messages.success(request, "Attendance record deleted successfully.")
        return super().post(request, *args, **kwargs)