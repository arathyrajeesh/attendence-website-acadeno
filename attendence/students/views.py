import io
import calendar
import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['months'] = list(enumerate(calendar.month_name))[1:]
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class StudentAttendanceDetailView(ListView):
    """All attendance records for a single student, with optional month/year filter."""
    model = Attendance
    template_name = 'students/student_attendance.html'
    context_object_name = 'attendances'

    def dispatch(self, request, *args, **kwargs):
        self.student = get_object_or_404(Student, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Attendance.objects.filter(student=self.student).order_by('date')
        month = self.request.GET.get('month', '')
        year  = self.request.GET.get('year',  '')
        if month and year:
            try:
                qs = qs.filter(date__month=int(month), date__year=int(year))
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendances = context['attendances']
        present = sum(1 for a in attendances if a.status == 'present')
        absent  = sum(1 for a in attendances if a.status == 'absent')
        no_class = sum(1 for a in attendances if a.status == 'no_class')
        total_class_days = present + absent
        pct = f"{(present / total_class_days * 100):.1f}%" if total_class_days else "N/A"
        
        context.update({
            'student':         self.student,
            'months':          list(enumerate(calendar.month_name))[1:],
            'selected_month':  self.request.GET.get('month', ''),
            'selected_year':   self.request.GET.get('year',  ''),
            'present_count':   present,
            'absent_count':    absent,
            'no_class_count':  no_class,
            'total_count':     len(attendances),
            'attendance_pct':  pct,
        })
        return context


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


# ── Export Helpers ─────────────────────────────────────────────────────────────

def _get_month_year(request):
    """Return (month, year) from GET params, or (None, None) for all-records export."""
    raw_month = request.GET.get('month', '').strip()
    raw_year  = request.GET.get('year',  '').strip()
    if not raw_month and not raw_year:
        return None, None               # caller should export all records
    today = datetime.date.today()
    try:
        month = int(raw_month) if raw_month else today.month
        year  = int(raw_year)  if raw_year  else today.year
        if not (1 <= month <= 12):
            month = today.month
    except (ValueError, TypeError):
        month, year = today.month, today.year
    return month, year


def export_student_pdf(request, pk):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    student = get_object_or_404(Student, pk=pk)
    month, year = _get_month_year(request)

    records = Attendance.objects.filter(student=student).order_by('date')
    if month and year:
        records = records.filter(date__year=year, date__month=month)
        period_label = f"{calendar.month_name[month]} {year}"
    else:
        period_label = "All Records"

    buf  = io.BytesIO()
    doc  = SimpleDocTemplate(buf, pagesize=A4,
                              topMargin=18*mm, bottomMargin=18*mm,
                              leftMargin=18*mm, rightMargin=18*mm)
    styles = getSampleStyleSheet()
    elems  = []

    elems.append(Paragraph("ATTENDANCE REPORT", styles['Title']))
    elems.append(Paragraph(f"{student.name}  —  {period_label}", styles['Heading2']))
    elems.append(Paragraph(f"Course: {student.course}  |  Duration: {student.duration_months} months",
                            styles['Normal']))
    elems.append(Spacer(1, 8*mm))

    data = [['Date', 'Mode', 'Login', 'Logout', 'Status']]
    present = 0
    absent = 0
    no_class = 0
    for r in records:
        if r.status == 'present':
            present += 1
        elif r.status == 'absent':
            absent += 1
        else:
            no_class += 1
        data.append([
            str(r.date),
            r.get_mode_display(),
            r.login_time.strftime('%H:%M') if r.login_time else '—',
            r.logout_time.strftime('%H:%M') if r.logout_time else '—',
            r.get_status_display(),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[38*mm, 30*mm, 24*mm, 24*mm, 24*mm])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.HexColor('#1a1a1d')),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
            ('FONTNAME',     (0, 0), (-1,  0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f7')]),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('PADDING',      (0, 0), (-1, -1), 5),
        ]))
        elems.append(t)
    else:
        elems.append(Paragraph("No attendance records for this period.", styles['Normal']))

    elems.append(Spacer(1, 8*mm))
    total_class_days = present + absent
    pct = f"{(present / total_class_days * 100):.1f}%" if total_class_days else "N/A"

    summary = Table(
        [['Present', 'Absent', 'No Class', 'Attendance %'],
         [str(present), str(absent), str(no_class), pct]],
        colWidths=[30*mm, 30*mm, 30*mm, 35*mm]
    )
    summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5b9cf6')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    elems.append(Paragraph("Summary", styles['Heading3']))
    elems.append(Spacer(1, 3*mm))
    elems.append(summary)

    doc.build(elems)
    buf.seek(0)

    period_slug = period_label.replace(' ', '_')
    fname = f"{student.name.replace(' ', '_')}_{period_slug}.pdf"
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response


def export_student_excel(request, pk):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    student = get_object_or_404(Student, pk=pk)
    month, year = _get_month_year(request)

    records = Attendance.objects.filter(student=student).order_by('date')
    if month and year:
        records = records.filter(date__year=year, date__month=month)
        period_label = f"{calendar.month_name[month]} {year}"
        tab_title = f"{calendar.month_name[month][:3]} {year}"
    else:
        period_label = "All Records"
        tab_title = "All Records"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = tab_title

    thin = Border(
        left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),  bottom=Side(style='thin', color='CCCCCC'),
    )
    center = Alignment(horizontal='center', vertical='center')

    # Title block
    for row, text in enumerate([
        "ATTENDANCE REPORT",
        f"{student.name}  —  {period_label}",
        f"Course: {student.course}  |  Duration: {student.duration_months} months",
    ], start=1):
        ws.merge_cells(f'A{row}:E{row}')
        ws[f'A{row}'] = text
        ws[f'A{row}'].alignment = center
        ws[f'A{row}'].font = Font(bold=(row == 1), size=(13 if row == 1 else 10))

    ws.append([])  # blank

    # Header row (row 5)
    headers = ['Date', 'Mode', 'Login', 'Logout', 'Status']
    ws.append(headers)
    hdr_fill = PatternFill('solid', fgColor='1A1A1D')
    for col in range(1, 6):
        c = ws.cell(row=5, column=col)
        c.fill = hdr_fill
        c.font = Font(color='FFFFFF', bold=True, size=9)
        c.alignment = center
        c.border = thin

    # Data
    present = 0
    absent = 0
    no_class = 0
    for i, r in enumerate(records, start=6):
        if r.status == 'present':
            present += 1
        elif r.status == 'absent':
            absent += 1
        else:
            no_class += 1

        ws.append([
            str(r.date), r.get_mode_display(),
            r.login_time.strftime('%H:%M') if r.login_time else '—',
            r.logout_time.strftime('%H:%M') if r.logout_time else '—',
            r.get_status_display(),
        ])
        bg = 'FFFFFF' if i % 2 == 0 else 'F5F5F7'
        row_fill = PatternFill('solid', fgColor=bg)
        for col in range(1, 6):
            c = ws.cell(row=i, column=col)
            c.fill = row_fill; c.border = thin; c.alignment = center
        # Colour status cell
        sc = ws.cell(row=i, column=5)
        status_color = '22C55E' if r.status == 'present' else ('EF4444' if r.status == 'absent' else 'F59E0B')
        sc.font = Font(color=status_color, bold=True, size=9)

    # Summary
    total_class_days = present + absent
    pct = f"{(present / total_class_days * 100):.1f}%" if total_class_days else "N/A"

    ws.append([])
    sr = ws.max_row + 1
    for col, val in enumerate(['Present', 'Absent', 'No Class', 'Attendance %', ''], start=1):
        c = ws.cell(row=sr, column=col, value=val)
        if col < 5:
            c.fill = PatternFill('solid', fgColor='5B9CF6')
            c.font = Font(color='FFFFFF', bold=True, size=9)
            c.alignment = center; c.border = thin
    for col, val in enumerate([present, absent, no_class, pct, ''], start=1):
        c = ws.cell(row=sr + 1, column=col, value=val)
        if col < 5:
            c.font = Font(bold=True, size=9)
            c.alignment = center; c.border = thin

    for col, w in zip('ABCDE', [14, 12, 10, 10, 10]):
        ws.column_dimensions[col].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    period_slug = period_label.replace(' ', '_')
    fname = f"{student.name.replace(' ', '_')}_{period_slug}.xlsx"
    response = HttpResponse(buf,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    return response