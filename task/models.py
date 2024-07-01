from django.db import models
from django.utils import timezone
from Authentication.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100, default='')
    description = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title
