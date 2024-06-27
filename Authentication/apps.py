from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    name = 'Authentication'

    def ready(self):
        from .signals import profile_signals
