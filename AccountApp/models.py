from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


number_validator = RegexValidator(
    regex=r'^\d{8}$',
    message='this number must contrain 8 digits',
)


def validate_birth_date(value):
    if value >= timezone.localdate():
        raise ValidationError("la date de naissance n'est pas valide")


class User(AbstractUser):
    pass


class Speciality(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Speciality"
        verbose_name_plural = "Specialities"

class Doctor(User):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        editable=False,
        related_name='doctor_profile',
        db_column='user_id',
    )
    license_number = models.CharField(
        max_length=6,
        unique=True,
        validators=[MinLengthValidator(6), MaxLengthValidator(6)],
    )
    phone = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    specialities = models.ManyToManyField(
        Speciality,
        related_name='doctors',
    )

    class Meta:
        verbose_name = "doctor"
        verbose_name_plural = "doctors"



class Patient(User):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        editable=False,
        related_name='patient_profile',
        db_column='user_id',
    )
    national_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[number_validator],
    )
    phone = models.CharField(max_length=8, validators=[number_validator])
    birth_date = models.DateField(validators=[validate_birth_date])
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "patient"
        verbose_name_plural = "patients"