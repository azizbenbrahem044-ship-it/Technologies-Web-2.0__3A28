from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import Appointment

class AppointmentStacked(admin.StackedInline):
    model = Appointment
    fk_name = "doctor"
    extra = 1
    show_change_link = True
    readonly_fields = ("created_at", "updated_at")


class AppointmentPatientInline(admin.StackedInline):
    model = Appointment
    fk_name = "patient"
    extra = 0
    show_change_link = True
    readonly_fields = ("created_at", "updated_at")


class DateRangeFilter(admin.SimpleListFilter):
    title = "Date du rendez-vous"
    parameter_name = "date_range"

    def lookups(self, request, model_admin):
        return (
            ("today", "Aujourd'hui"),
            ("week", "Cette semaine"),
            ("upcoming", "À venir"),
        )

    def queryset(self, request, queryset):
        today = timezone.localdate()
        if self.value() == "today":
            return queryset.filter(appointment_date__date=today)
        if self.value() == "week":
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            return queryset.filter(
                appointment_date__date__range=(week_start, week_end)
            )
        if self.value() == "upcoming":
            return queryset.filter(appointment_date__gt=timezone.now())
        return queryset


@admin.register(Appointment)
class AppointmentAdminPers(admin.ModelAdmin):
    list_display = (
        "appointment_date",
        "doctor_name",
        "patient_name",
        "duration_minutes",
        "status",
    )
    list_filter = ("status", "doctor", DateRangeFilter)
    list_editable = ("status",)
    search_fields = (
        "patient__last_name",
        "patient__first_name",
        "patient__national_id",
        "doctor__last_name",
        "doctor__first_name",
        "doctor__license_number",
    )
    ordering = ("-appointment_date",)
    list_per_page = 2
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Participants", {"fields": ("doctor", "patient")}),
        (
            "Planification",
            {"fields": ("appointment_date", "duration_minutes", "status")},
        ),
        ("Dossier", {"fields": ("reason", "prescription")}),
        ("Suivi", {"fields": ("created_at", "updated_at")}),
    )
    actions = ("confirm_selected", "cancel_selected")

    @admin.display(description="Médecin", ordering="doctor__last_name")
    def doctor_name(self, obj):
        return obj.doctor.get_full_name() or obj.doctor.username

    @admin.display(description="Patient", ordering="patient__last_name")
    def patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    @admin.action(description="make them confirmed")
    def confirm_selected(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.CONFIRMED)
        self.message_user(request, f"{updated} rendez-vous confirmé(s).")

    @admin.action(description="Annuler les rendez-vous sélectionnés")
    def cancel_selected(self, request, queryset):
        updated = queryset.update(status=Appointment.Status.CANCELED)
        self.message_user(request, f"{updated} rendez-vous annulé(s).")