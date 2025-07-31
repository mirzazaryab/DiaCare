from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [('patient', 'Patient'), ('doctor', 'Doctor')]
    DIABETES_TYPE = [('type1', 'Type 1'), ('type2', 'Type 2'), ('none', 'None')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    diabetes_type = models.CharField(max_length=10, choices=DIABETES_TYPE, default='none')
    medications = models.TextField(blank=True)

class GlucoseLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    fasting = models.FloatField(null=True, blank=True)
    postprandial = models.FloatField(null=True, blank=True)
    hba1c = models.FloatField(null=True, blank=True)

class MealLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    carbs = models.FloatField()
    calories = models.FloatField()

class ActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    activity_type = models.CharField(max_length=50)

class Summary(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    text = models.TextField()

class DoctorNote(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_notes')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_notes')
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.TextField()

class Consent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    consent_given = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)