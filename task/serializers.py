import django_filters
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = ['id','Title','Description','assigned_to','Completed']

class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = ['Title', 'Description', 'Completed', 'due_date']
