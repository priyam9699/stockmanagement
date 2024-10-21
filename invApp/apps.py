from django.apps import AppConfig

class InvappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'invApp'

    def ready(self):
        import invApp.signals  # Import signals to ensure they're registered
