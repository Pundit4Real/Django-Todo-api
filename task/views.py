from django.template.loader import render_to_string
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer,FeedbackSerializer

class TaskCreate(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['completed', 'title']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'completed']
    ordering = ['title']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-id')

class TaskRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TaskDestroy(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

# feedback/views.py (updated)

class FeedbackView(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            message = serializer.validated_data['message']
            
            subject = f"New Feedback Received from {username}"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [settings.FEEDBACK_EMAIL]
            
            html_content = render_to_string('Auth_email/feedback.html', {
                'username': username,
                'email': email,
                'message': message,
            })
            
            email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            return Response({'message': 'Thank you for your feedback! We appreciate you taking the time to share your thoughts with us'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
