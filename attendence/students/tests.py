from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from datetime import date, time

from .models import Student, Attendance
from .forms import AttendanceForm, StudentForm

class StudentModelTests(TestCase):
    def test_student_creation(self):
        student = Student.objects.create(
            name="John Doe",
            course="Python Web Development",
            duration_months=6
        )
        self.assertEqual(str(student), "John Doe")
        self.assertIsNotNone(student.joined_date)

class AttendanceModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Jane Doe",
            course="Data Science",
            duration_months=3
        )

    def test_attendance_creation(self):
        record = Attendance.objects.create(
            student=self.student,
            date=date(2026, 7, 16), # Thursday
            mode="online",
            login_time=time(9, 0),
            logout_time=time(17, 0),
            status="present"
        )
        self.assertEqual(str(record), "Jane Doe - 2026-07-16")
        self.assertTrue(record.is_present)

    def test_attendance_unique_together_constraint(self):
        Attendance.objects.create(
            student=self.student,
            date=date(2026, 7, 16),
            mode="online"
        )
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                student=self.student,
                date=date(2026, 7, 16),
                mode="offline"
            )

class AttendanceFormTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Bob Smith",
            course="UI/UX Design",
            duration_months=4
        )

    def test_form_validation_correct_times(self):
        form_data = {
            'student': self.student.id,
            'date': '2026-07-16', # Thursday
            'mode': 'offline',
            'login_time': '09:00:00',
            'logout_time': '10:00:00',
            'status': 'present'
        }
        form = AttendanceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_invalid_times(self):
        form_data = {
            'student': self.student.id,
            'date': '2026-07-16',
            'mode': 'offline',
            'login_time': '10:00:00',
            'logout_time': '09:00:00',
            'status': 'present'
        }
        form = AttendanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], "Logout time must be after login time.")

    def test_form_validation_sunday(self):
        form_data = {
            'student': self.student.id,
            'date': '2026-07-19', # Sunday
            'mode': 'offline',
            'status': 'present'
        }
        form = AttendanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], "Sunday has no class.")

class StudentViewsTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Alice",
            course="Cybersecurity",
            duration_months=12
        )

    def test_student_list_view(self):
        response = self.client.get(reverse('student-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertTemplateUsed(response, 'students/student_list.html')

    def test_student_create_view(self):
        post_response = self.client.post(reverse('student-list'), {
            'name': 'Charlie',
            'course': 'Networking',
            'duration_months': 6
        })
        self.assertRedirects(post_response, reverse('student-list'))
        self.assertEqual(Student.objects.count(), 2)

    def test_student_update_view(self):
        post_response = self.client.post(reverse('student-update', args=[self.student.id]), {
            'name': 'Alice Updated',
            'course': 'Cybersecurity II',
            'duration_months': 12
        })
        self.assertRedirects(post_response, reverse('student-list'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Alice Updated')

    def test_student_delete_view(self):
        post_response = self.client.post(reverse('student-delete', args=[self.student.id]))
        self.assertRedirects(post_response, reverse('student-list'))
        self.assertEqual(Student.objects.count(), 0)

class AttendanceViewsTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="David",
            course="Product Management",
            duration_months=2
        )
        self.attendance = Attendance.objects.create(
            student=self.student,
            date=date(2026, 7, 15), # Wednesday
            mode="offline",
            status="present"
        )

    def test_attendance_list_view_and_filtering(self):
        response = self.client.get(reverse('attendance-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "David")

        filter_response = self.client.get(reverse('attendance-list'), {'date': '2026-07-15'})
        self.assertEqual(filter_response.status_code, 200)
        self.assertContains(filter_response, "David")

        no_match_response = self.client.get(reverse('attendance-list'), {'date': '2000-01-01'})
        self.assertEqual(no_match_response.status_code, 200)
        self.assertNotContains(no_match_response, 'class="text-accent fw-500">David</td>')

    def test_attendance_create_view(self):
        post_response = self.client.post(reverse('attendance-list'), {
            'student': self.student.id,
            'date': '2026-07-16', # Thursday
            'mode': 'online',
            'status': 'present'
        })
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.assertEqual(Attendance.objects.count(), 2)

    def test_attendance_update_view(self):
        post_response = self.client.post(reverse('attendance-update', args=[self.attendance.id]), {
            'student': self.student.id,
            'date': '2026-07-15',
            'mode': 'online',
            'status': 'absent'
        })
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.attendance.refresh_from_db()
        self.assertEqual(self.attendance.mode, 'online')
        self.assertEqual(self.attendance.status, 'absent')

    def test_attendance_delete_view(self):
        post_response = self.client.post(reverse('attendance-delete', args=[self.attendance.id]))
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.assertEqual(Attendance.objects.count(), 0)
