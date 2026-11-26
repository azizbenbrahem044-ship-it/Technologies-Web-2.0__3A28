from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from AppointmentApp.admin import AppointmentPatientInline, AppointmentStacked

from .models import Doctor, Patient, Speciality, User


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "license_number", "phone")
    list_filter = ("specialities",)
    search_fields = (
        "license_number",
        "last_name",
        "first_name",
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
        ("Médecin", {"fields": ("license_number", "phone", "specialities")}),
    )
    inlines = [AppointmentStacked]


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
    inlines = [AppointmentPatientInline]


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "email")},
        ),
    )