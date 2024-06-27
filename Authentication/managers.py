from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

  def _create_user(self, email, username, password, is_active, is_staff, is_superuser, **extra_fields):

    if not email:
        raise ValueError(_('The Email field must be set'))
    
    if '@' not in email or '.com' not in email:
        raise ValueError(_('Invalid email address'))

    now = timezone.now()
    email = self.normalize_email(email)

    user = self.model(
        email=email,
        username=username,
        is_staff=is_staff, 
        is_active=is_active,
        is_superuser=is_superuser, 
        last_login=now,
        date_joined=now, 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password,username=None, **extra_fields):
    return self._create_user(email, username, password,False, False, False, **extra_fields)

  def create_superuser(self, email, username, password, **extra_fields):
    user=self._create_user(email, username, password, True,True, True, **extra_fields)
    user.save(using=self._db)
    
    return user    