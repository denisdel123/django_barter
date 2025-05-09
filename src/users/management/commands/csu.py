from django.core.management import BaseCommand

from django.contrib.auth.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin',
            first_name='Denis',
            last_name='Belenko',
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )

        user.set_password('admin')
        user.save()
