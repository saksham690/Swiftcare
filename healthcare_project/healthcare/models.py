from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    dob = models.CharField(max_length=10)
    password = models.CharField(max_length=200)

    username = models.CharField(max_length=150, unique=True, default='')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='healthcare_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='healthcare_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Doctor(models.Model):
    name = models.CharField(max_length=200)
    speciality = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    experience = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    virtual_visit = models.BooleanField(default=False)
    image_url = models.URLField()
    distance = models.FloatField(blank=True, null=True)
    temp_dummy = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.name

class helathcare_doctor(models.Model):
    name = models.CharField(max_length=200)
    speciality = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    experience = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    virtual_visit = models.BooleanField(default=False)
    image_url = models.CharField(max_length=200, blank=True, default='images/d10.jpg')
    distance = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor_id = models.IntegerField()
    requested_date = models.CharField(max_length=10)
    status = models.CharField(max_length=20, default='Pending')
    new_date = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Appointment for {self.patient} on {self.requested_date}"

class Response(models.Model):
    status = models.CharField(max_length=120)
    new_date = models.CharField(max_length=200)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Response: {self.status}"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.user or self.doctor}"