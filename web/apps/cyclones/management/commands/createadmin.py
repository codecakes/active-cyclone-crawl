"""Create super user equivalent command."""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    """Management command to generate super admin user."""

    def handle(self, *args, **options):
        """Generate super admin."""
        User = get_user_model()
        if not User.objects.filter(username='superadmin').exists():
            u = User.objects.create_superuser(
            'superadmin', 'akulmat@protonmail.com', 'superadmin')
            u.is_active = True
            u.is_admin = True
            u.save()
            settings.LOGGER.info("Super admin created.")
        else:
            settings.LOGGER.warn("Super admin already exists.")
