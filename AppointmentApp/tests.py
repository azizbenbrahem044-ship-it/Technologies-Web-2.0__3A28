from datetime import date, timedelta

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.utils import timezone

from AccountApp.models import Doctor, Patient, Speciality, User
from AppointmentApp.admin import AppointmentAdmin, DateRangeFilter
from AppointmentApp.models import Appointment


class AppointmentModelsAndAdminTests(TestCase):
    def setUp(self):
        self.spec = Speciality.objects.create(name="Dermatologie")
        self.doctor = Doctor.objects.create_user(
            username="doc_appt",
            password="Password123!",
            first_name="Leila",
            last_name="Trabelsi",
            license_number="222222",
            phone="21112233",
        )
        self.patient = Patient.objects.create_user(
            username="pat_appt",
            password="Password123!",
            first_name="Salma",
            last_name="Ayari",
            national_id="11223344",
            phone="50112233",
            birth_date=date(1992, 3, 15),
        )

    def test_appointment_date_validation_and_past_modification(self):
        past_dt = timezone.now() - timedelta(days=1)
        past_appt = Appointment(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=past_dt,
            reason="Consultation",
        )
        with self.assertRaises(ValidationError) as ctx:
            past_appt.full_clean()
        self.assertIn("appointment_date", ctx.exception.message_dict)

        # Save an existing past appointment (e.g. legacy data) and verify status update passes clean()
        past_appt.save()
        past_appt.status = Appointment.Status.CONFIRMED
        past_appt.full_clean()

        # Modifying date to another past date still fails
        past_appt.appointment_date = past_dt - timedelta(hours=2)
        with self.assertRaises(ValidationError):
            past_appt.full_clean()

    def test_prescription_pdf_only(self):
        future_dt = timezone.now() + timedelta(days=2)
        bad_file = SimpleUploadedFile("note.txt", b"hello", content_type="text/plain")
        appt = Appointment(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=future_dt,
            reason="Ordonnance",
            prescription=bad_file,
        )
        with self.assertRaises(ValidationError) as ctx:
            appt.full_clean()
        self.assertIn("prescription", ctx.exception.message_dict)

    def test_unique_doctor_appointment_date_constraint(self):
        future_dt = timezone.now() + timedelta(days=3)
        Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=future_dt,
            reason="First",
        )
        with self.assertRaises(IntegrityError):
            Appointment.objects.create(
                doctor=self.doctor,
                patient=self.patient,
                appointment_date=future_dt,
                reason="Duplicate slot",
            )

    def test_admin_actions_and_date_filter(self):
        now = timezone.now()
        a1 = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=now + timedelta(hours=1),
            reason="A1",
        )
        a2 = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            appointment_date=now + timedelta(days=2),
            reason="A2",
        )

        admin_instance = AppointmentAdmin(Appointment, AdminSite())
        request = RequestFactory().get("/admin/AppointmentApp/appointment/")
        request.user = User.objects.create_superuser(
            username="admin_test", password="Password123!", email="a@b.com"
        )
        from django.contrib.messages.storage.fallback import FallbackStorage

        setattr(request, "session", "session")
        setattr(request, "_messages", FallbackStorage(request))

        qs = Appointment.objects.filter(pk__in=[a1.pk, a2.pk])
        admin_instance.confirm_selected(request, qs)
        self.assertTrue(
            all(
                s == Appointment.Status.CONFIRMED
                for s in qs.values_list("status", flat=True)
            )
        )

        admin_instance.cancel_selected(request, qs)
        self.assertTrue(
            all(
                s == Appointment.Status.CANCELLED
                for s in qs.values_list("status", flat=True)
            )
        )

        flt = DateRangeFilter(
            request, {"date_range": "upcoming"}, Appointment, admin_instance
        )
        self.assertEqual(flt.queryset(request, Appointment.objects.all()).count(), 2)

    def test_secretary_group_permissions_in_admin(self):
        group = Group.objects.create(name="Secrétaires")
        appt_ct = ContentType.objects.get_for_model(Appointment)
        doc_ct = ContentType.objects.get_for_model(Doctor)
        pat_ct = ContentType.objects.get_for_model(Patient)
        spec_ct = ContentType.objects.get_for_model(Speciality)
        perms = (
            Permission.objects.filter(
                content_type=appt_ct,
                codename__in=["view_appointment", "add_appointment", "change_appointment"],
            )
            | Permission.objects.filter(content_type=doc_ct, codename="view_doctor")
            | Permission.objects.filter(content_type=pat_ct, codename="view_patient")
            | Permission.objects.filter(content_type=spec_ct, codename="view_speciality")
        )
        group.permissions.set(perms)

        sec = User.objects.create_user(
            username="sec_test",
            password="Password123!",
            is_staff=True,
            is_superuser=False,
        )
        sec.groups.add(group)

        self.client.force_login(sec)
        self.assertEqual(self.client.get("/admin/AppointmentApp/appointment/").status_code, 200)
        self.assertEqual(self.client.get("/admin/AppointmentApp/appointment/add/").status_code, 200)
        self.assertEqual(self.client.get("/admin/AccountApp/doctor/").status_code, 200)
        self.assertEqual(self.client.get("/admin/AccountApp/doctor/add/").status_code, 403)
        self.assertEqual(self.client.get("/admin/AccountApp/patient/add/").status_code, 403)
        self.assertEqual(self.client.get("/admin/AccountApp/speciality/add/").status_code, 403)
