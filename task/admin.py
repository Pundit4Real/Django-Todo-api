from django.contrib import admin
from task.models import Task

# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title','completed','date_created']