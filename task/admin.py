from django.contrib import admin
from task.models import Task

# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display = ['title','id','date_created','completed']

admin.site.register(Task,TaskAdmin)