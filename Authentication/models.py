from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin
from .managers import UserManager


# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=200)
    email_verification_code = models.CharField(max_length=50, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

def save(self, *args, **kwargs):
    if not self.pk:  # Check if the object is being created for the first time
        created = True
    else:
        created = False

    if created:
        # Hash the password if it's set and not hashed already
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)

    super(User,self).save(*args, **kwargs)

    if created:
        # Create UserProfile if it doesn't exist
        if not hasattr(self, 'userprofile'):
            UserProfile.objects.create(user=self)

    def __str__(self):
        if self.username:
            return self.username
        else:
            return self.email  
        
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')
    full_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)