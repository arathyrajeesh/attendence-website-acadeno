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
            date=date(2026, 7, 16),
            mode="online",
            login_time=time(9, 0),
            logout_time=time(17, 0),
            is_present=True
        )
        self.assertEqual(str(record), "Jane Doe - 2026-07-16")

    def test_attendance_unique_together_constraint(self):
        Attendance.objects.create(
            student=self.student,
            date=date(2026, 7, 16),
            mode="online"
        )
        # Attempting to create duplicate record for the same student on the same day should fail
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
            'date': '2026-07-16',
            'mode': 'offline',
            'login_time': '09:00:00',
            'logout_time': '10:00:00',
            'is_present': True
        }
        form = AttendanceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_invalid_times(self):
        form_data = {
            'student': self.student.id,
            'date': '2026-07-16',
            'mode': 'offline',
            'login_time': '10:00:00',
            'logout_time': '09:00:00', # Logout before login
            'is_present': True
        }
        form = AttendanceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('logout_time', form.errors)
        self.assertEqual(form.errors['logout_time'][0], "Logout time must be after the login time.")

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
        response = self.client.get(reverse('student-create'))
        self.assertEqual(response.status_code, 200)
        
        post_response = self.client.post(reverse('student-create'), {
            'name': 'Charlie',
            'course': 'Networking',
            'duration_months': 6
        })
        # Check redirect on success
        self.assertRedirects(post_response, reverse('student-list'))
        self.assertEqual(Student.objects.count(), 2)

    def test_student_update_view(self):
        response = self.client.get(reverse('student-update', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(reverse('student-update', args=[self.student.id]), {
            'name': 'Alice Updated',
            'course': 'Cybersecurity II',
            'duration_months': 12
        })
        self.assertRedirects(post_response, reverse('student-list'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Alice Updated')

    def test_student_delete_view(self):
        response = self.client.get(reverse('student-delete', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

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
            date=date(2026, 7, 16),
            mode="offline",
            is_present=True
        )

    def test_attendance_list_view_and_filtering(self):
        # View list
        response = self.client.get(reverse('attendance-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "David")

        # Filter by date with matches
        filter_response = self.client.get(reverse('attendance-list'), {'date': '2026-07-16'})
        self.assertEqual(filter_response.status_code, 200)
        self.assertContains(filter_response, "David")

        # Filter by date without matches
        no_match_response = self.client.get(reverse('attendance-list'), {'date': '2026-07-17'})
        self.assertEqual(no_match_response.status_code, 200)
        self.assertNotContains(no_match_response, "David")

    def test_attendance_create_view(self):
        post_response = self.client.post(reverse('attendance-create'), {
            'student': self.student.id,
            'date': '2026-07-17',
            'mode': 'online',
            'is_present': True
        })
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.assertEqual(Attendance.objects.count(), 2)

    def test_attendance_update_view(self):
        post_response = self.client.post(reverse('attendance-update', args=[self.attendance.id]), {
            'student': self.student.id,
            'date': '2026-07-16',
            'mode': 'online', # changed from offline
            'is_present': False # changed from True
        })
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.attendance.refresh_from_db()
        self.assertEqual(self.attendance.mode, 'online')
        self.assertFalse(self.attendance.is_present)

    def test_attendance_delete_view(self):
        post_response = self.client.post(reverse('attendance-delete', args=[self.attendance.id]))
        self.assertRedirects(post_response, reverse('attendance-list'))
        self.assertEqual(Attendance.objects.count(), 0)
