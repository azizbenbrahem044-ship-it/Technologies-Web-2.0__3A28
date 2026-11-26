from django.db import models
from django.db.models import CASCADE
from AccountApp.models import Doctor, Patient
from django.utils import timezone
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "en attente"
        CONFIRMED = "CONFIRMED", "confirmé"
        CANCELED = "CANCELED", "annulé"

    reason = models.TextField()
    prescription = models.FileField(
        blank=True,
        upload_to='prescriptions/'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    appointment_date = models.DateTimeField()
    doctor = models.ForeignKey(
        Doctor,
        to_field="user",
        on_delete=CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        Patient,
        to_field="user",
        on_delete=CASCADE,
        related_name='appointments'
    )

    def clean(self):
        super().clean()
        if self._state.adding:
            date_changed = True
        else:
            original_date = Appointment.objects.filter(pk=self.pk).values_list(
                "appointment_date", flat=True
            ).first()
            date_changed = original_date != self.appointment_date

        if (
            date_changed
            and self.appointment_date
            and self.appointment_date <= timezone.now()
        ):
            raise ValidationError("Appointment date cannot be in the past.")

    def __str__(self):
        patient = self.patient.get_full_name() or self.patient.username
        doctor = self.doctor.get_full_name() or self.doctor.username
        return f"Rendez-vous de {patient} avec Dr {doctor} le {self.appointment_date:%d/%m/%Y %H:%M}"

    class Meta:
        ordering = ['-appointment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_appointment_per_doctor',
                violation_error_message='This doctor already has an appointment at this date and time.'
            )
        ]