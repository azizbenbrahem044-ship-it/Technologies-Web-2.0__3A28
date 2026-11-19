from django.db import models
from django.db.models import CASCADE
from AccountApp.models import Doctor,Patient
# Create your models here.
class Appointment(models.Model):
    reason = models.TextField()
    prescription = models.FileField(
        blank=True, 
        upload_to='prescriptions/'
    )
    class Status = (models.TextChoices):
    PENDING = "PENDING", "en attente"
    CONFIRMED = "CONFIRMED", "confirmé"
    CANCELED = "CANCELED", "annulé"
    status = models.charfield(max_length=10,choices=Status.choices, default=Status.PENDING)
    #status = models.CharField(max_length=10, choices=[("PENDING",En a)])
    duration_minutes = models.PositiveBigIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    appointment_date = models.DateTimeField()
    doctor = models.ForeignKey(Doctor,on_delete=models,CASCADE,related_name= 'appointment')
    patient = models.ForeignKey(Patient,on_delete=models,CASCADE,related_name= 'appointment')
    



