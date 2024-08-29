from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, 
                                    validators=[RegexValidator(regex=r'^\d{10,15}$', message="Phone number must be between 10 and 15 digits.")])
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, 
                                    validators=[RegexValidator(regex=r'^\d{10,15}$', message="Phone number must be between 10 and 15 digits.")])
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    otp = models.CharField(max_length=6, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=50, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def save(self, *args, **kwargs):
        # Get the current instance of the user (if it exists) before saving
        old_user = User.objects.filter(id=self.id).first()
        super(User, self).save(*args, **kwargs)  # Save the user first

        # Check if the role has changed or if this is a new user
        if old_user and old_user.role != self.role:
            # If the user was a patient and their role is now doctor, create the DoctorProfile
            if self.role == 'doctor' and not hasattr(self, 'doctor_profile'):
                DoctorProfile.objects.create(user=self)

            # If the user was a doctor and their role is now patient, create the PatientProfile
            elif self.role == 'patient' and not hasattr(self, 'patient_profile'):
                PatientProfile.objects.create(user=self)

            # If the user was a doctor or patient and now their role is receptionist
            elif self.role == 'receptionist' and not hasattr(self, 'receptionist_profile'):
                ReceptionistProfile.objects.create(user=self)    

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='doctor_pics/', blank=True)
    experience = models.PositiveIntegerField(default=0)  # Years of experience
    qualification = models.CharField(max_length=255, blank=True)  # Example: "MBBS, MD (Internal Medicine)"

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.middle_name} - {self.specialization}"

    def get_availability(self, date):
        return self.availabilities.filter(date=date)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.middle_name}"

class ReceptionistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receptionist_profile')

    def __str__(self):
        return f"{self.user.first_name} {self.user.middle_name}"
