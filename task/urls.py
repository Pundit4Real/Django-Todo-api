from django.urls import path
from .views import TaskCreate, TaskList, TaskRetrieveUpdate, TaskDestroy

urlpatterns = [
    path('tasks/', TaskList.as_view(), name='task-list'),
    path('tasks/create/', TaskCreate.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdate.as_view(), name='task-retrieve-update'),
    path('tasks/<int:pk>/delete/', TaskDestroy.as_view(), name='task-destroy'),
]
 