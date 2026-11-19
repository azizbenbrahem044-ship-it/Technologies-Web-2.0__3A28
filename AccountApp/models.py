from django.contrib.postgres import validators
from django.db import models
From django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator,MaxLengthValidator,RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class User (AbstractUser):
    pass
 class Speciality(models.Model):
        name = models.CharField(max_length=255)
        created_at = models.DateTimeField(auto_now_add=True)
        update_at = models.DateTimeField(auto_now=True)
        

class Doctor(user):
    license_number = models.CharField(max_length=6,unique=True validators=[MinLengthValidator(6),MaxLengthValidator(6)])
    phone = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    specialities = models.ManyToManyField(
        Speciality,
        related_name="doctors"
    )
number_validator = RegexValidator(
     regex=r'^\d{8}$',
     message='this number must contrain 8 digits'
)
def validate_birth_date(v):
     if v>=timezone.localdate():
          raise ValidationError("la date de naissance n'est pas valide")
class Patient(user):
    national_id = models.CharField(max_length=8,unique=True,validators=[number_validator])
    phone = models.CharField(max_length=8,validators=[number_validator])
    birth_date = models.DateField(validators=validate_birth_date)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

   