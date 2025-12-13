from django.core.management.base import BaseCommand

from apps.rbac.models import Permission, Role


class Command(BaseCommand):
    help = "Seed the permissions catalog and default roles."

    def handle(self, *args, **options):
        # Remove all existing permissions and roles
        Permission.objects.all().delete()
        Role.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Permissions and roles cleared (disabled)."))
