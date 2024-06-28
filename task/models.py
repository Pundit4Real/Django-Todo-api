from django.db import models
from django.utils import timezone
from Authentication.models import User
# Create your models here.

class Task(models.Model):
    Title = models.CharField(max_length=100,default='')
    Description = models.TextField()
    Date_created = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=timezone.now)
    Completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.Title