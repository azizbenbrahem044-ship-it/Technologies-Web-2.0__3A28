from datetime import date, timedelta

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from AccountApp.admin import DoctorAdmin, PatientAdmin
from AccountApp.models import Doctor, Patient, Speciality, User
from AppointmentApp.admin import AppointmentInline
from AppointmentApp.models import Appointment


class AccountModelsAndAdminTests(TestCase):
    def setUp(self):
        self.spec = Speciality.objects.create(name="Cardiologie")
        self.doctor = Doctor.objects.create_user(
            username="doc1",
            password="Password123!",
            first_name="Sami",
            last_name="Ben Ali",
            license_number="123456",
            phone="22112233",
        )
        self.doctor.specialities.add(self.spec)
        self.patient = Patient.objects.create_user(
            username="pat1",
            password="Password123!",
            first_name="Amine",
            last_name="Khelifi",
            national_id="12345678",
            phone="55112233",
            birth_date=date(1995, 5, 10),
        )

    def test_profile_pk_matches_user_pk(self):
        self.assertTrue(User.objects.filter(pk=self.doctor.pk).exists())
        self.assertTrue(User.objects.filter(pk=self.patient.pk).exists())
        self.assertEqual(self.doctor.user_id, self.doctor.pk)
        self.assertEqual(self.patient.user_id, self.patient.pk)

    def test_doctor_validators(self):
        invalid_license = Doctor(
            username="doc_bad_lic",
            license_number="123",
            phone="22112233",
        )
        with self.assertRaises(ValidationError) as ctx:
            invalid_license.full_clean()
        self.assertIn("license_number", ctx.exception.message_dict)

        invalid_phone = Doctor(
            username="doc_bad_phone",
            license_number="654321",
            phone="1234",
        )
        with self.assertRaises(ValidationError) as ctx:
            invalid_phone.full_clean()
        self.assertIn("phone", ctx.exception.message_dict)

    def test_patient_validators(self):
        invalid_cin = Patient(
            username="pat_bad_cin",
            national_id="1234",
            phone="22112233",
            birth_date=date(1990, 1, 1),
        )
        with self.assertRaises(ValidationError) as ctx:
            invalid_cin.full_clean()
        self.assertIn("national_id", ctx.exception.message_dict)

        future_birth = Patient(
            username="pat_bad_birth",
            national_id="87654321",
            phone="22112233",
            birth_date=timezone.localdate(),
        )
        with self.assertRaises(ValidationError) as ctx:
            future_birth.full_clean()
        self.assertIn("birth_date", ctx.exception.message_dict)

    def test_admin_readonly_fields_and_today_duration(self):
        site = AdminSite()
        doc_admin = DoctorAdmin(Doctor, site)
        pat_admin = PatientAdmin(Patient, site)
        request = RequestFactory().get("/admin/")

        self.assertEqual(doc_admin.get_readonly_fields(request, None), ())
        self.assertEqual(
            doc_admin.get_readonly_fields(request, self.doctor),
            ("license_number",),
        )
        self.assertEqual(pat_admin.get_readonly_fields(request, None), ())
        self.assertEqual(
            pat_admin.get_readonly_fields(request, self.patient),
            ("national_id",),
        )
        self.assertIn(AppointmentInline, pat_admin.inlines)

        now = timezone.now()
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=now + timedelta(minutes=10),
            duration_minutes=45,
            status=Appointment.Status.CONFIRMED,
            reason="Test",
        )
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=now + timedelta(minutes=40),
            duration_minutes=30,
            status=Appointment.Status.PENDING,
            reason="Test pending",
        )
        self.assertEqual(doc_admin.today_confirmed_duration(self.doctor), 45)
