from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, iin, first_name, last_name, b_day, gender, password=None, **extra_fields):
        from .models import Gender
        gender_instance = Gender.objects.get(id=gender)
        user = self.model(iin=iin, first_name=first_name, last_name=last_name, 
                          b_day=b_day, gender=gender_instance, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, iin, first_name, last_name, b_day, gender, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(iin, first_name, last_name, b_day, gender, password, **extra_fields)


class Gender(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.name}"
    
class UserRole(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class User(AbstractUser):
    username = None
    iin = models.CharField(max_length=12, unique=True, primary_key=True)
    father_name = models.CharField(max_length=256, null=True, blank=True)
    b_day = models.DateField()
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=True,default=1)
    
    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'b_day', 'gender']

    objects = UserManager()

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.father_name}"