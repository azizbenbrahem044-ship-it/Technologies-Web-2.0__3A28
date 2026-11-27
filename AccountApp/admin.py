from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum
from django.utils import timezone

from AppointmentApp.admin import AppointmentInline, AppointmentStacked
from AppointmentApp.models import Appointment

from .models import Doctor, Patient, Speciality, User


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "license_number",
        "phone",
        "today_confirmed_duration",
    )
    list_filter = ("specialities",)
    search_fields = (
        "license_number",
        "last_name",
        "first_name",
    )
    ordering = ("last_name",)
    filter_horizontal = ("specialities",)
    fieldsets = (
        (
            "Compte",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Médecin", {"fields": ("license_number", "phone", "specialities")}),
    )
    inlines = [AppointmentStacked]

    def get_readonly_fields(self, request, obj=None):
        return ("license_number",) if obj else ()

    @admin.display(description="Durée confirmée du jour (min)")
    def today_confirmed_duration(self, obj):
        total = (
            obj.appointments.filter(
                status=Appointment.Status.CONFIRMED,
                appointment_date__date=timezone.localdate(),
            ).aggregate(total=Sum("duration_minutes"))["total"]
            or 0
        )
        return total


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "national_id",
        "phone",
        "birth_date",
    )
    search_fields = (
        "last_name",
        "first_name",
        "national_id",
    )
    ordering = ("last_name",)
    fieldsets = (
        (
            "Compte",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Patient", {"fields": ("national_id", "phone", "birth_date")}),
    )
    inlines = [AppointmentInline]

    def get_readonly_fields(self, request, obj=None):
        return ("national_id",) if obj else ()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "email")},
        ),
    )