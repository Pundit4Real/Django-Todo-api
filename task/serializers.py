import django_filters
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = ['id','title','description','assigned_to','completed']

class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'due_date']
