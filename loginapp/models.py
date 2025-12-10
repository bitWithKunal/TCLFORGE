from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
import random


# ---------------- USER MANAGER ----------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None):
        if not email:
            raise ValueError("Email is required")

        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username="admin"):
        user = self.create_user(email=email, password=password, username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ---------------- USER MODEL ----------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    # -------- PASSWORD VALIDATION --------
    def validate_strong_password(self, password):
        if len(password) < 7:
            raise ValidationError("Password must be at least 7 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one capital letter.")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")

    def set_password(self, raw_password):
        self.validate_strong_password(raw_password)
        super().set_password(raw_password)

# class PasswordResetOTP(models.Model):
#     user = models.ForeignKey("loginapp.User", on_delete=models.CASCADE)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_used = models.BooleanField(default=False)

#     # -----------------------------
#     # GENERATE OTP (6 digits)
#     # -----------------------------
#     @staticmethod
#     def create_otp(user):
#         otp = str(random.randint(100000, 999999))  # 6-digit OTP
#         otp_obj = PasswordResetOTP.objects.create(user=user, otp=otp)
#         return otp_obj

#     # -----------------------------
#     # CHECK OTP EXPIRED (5 minutes)
#     # -----------------------------
#     def is_expired(self):
#         return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

#     # -----------------------------
#     # VERIFY OTP (valid + unused)
#     # -----------------------------
#     def verify(self, entered_otp):
#         if self.otp != entered_otp:
#             return False

#         if self.is_used:
#             return False

#         if self.is_expired():
#             return False

#         return True

#     # -----------------------------
#     # MARK OTP AS USED
#     # -----------------------------
#     def mark_used(self):
#         self.is_used = True
#         self.save()

#     def __str__(self):
#         return f"{self.user.email} - {self.otp}"