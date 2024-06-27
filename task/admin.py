from django.contrib import admin
from task.models import Task

# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display = ['Title','id','Date_created','Completed']

admin.site.register(Task,TaskAdmin)