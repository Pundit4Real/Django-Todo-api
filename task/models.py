from django.db import models

# Create your models here.

class Task(models.Model):
    Title = models.CharField(max_length=100,default='')
    Description = models.TextField()
    Date_created = models.DateTimeField(auto_created=True)
    Completed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.Title