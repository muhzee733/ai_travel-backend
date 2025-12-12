from django.core.management.base import BaseCommand

from apps.rbac.models import Permission, Role

MODULE_PERMISSIONS = {
    "settings": ["view", "create", "update", "delete", "report", "manage"],
    "reports": ["view", "create", "update", "delete", "report"],
    "hotels": ["view", "create", "update", "delete", "report"],
    "cars": ["view", "create", "update", "delete", "report"],
    "packages": ["view", "create", "update", "delete", "report"],
    "earning": ["view", "create", "update", "delete", "report"],
    "airtickets": ["view", "create", "update", "delete", "report"],
    "visa": ["view", "create", "update", "delete", "report"],
}

RBAC_EXTRA_CODES = [
    "rbac.manage_roles",
    "rbac.manage_users",
    "rbac.view_permissions",
]

CUSTOMER_PERMISSION_CODES = [
    "hotels.view",
    "cars.view",
    "packages.view",
    "airtickets.view",
    "visa.view",
    "earning.view",
    "reports.view",
]


class Command(BaseCommand):
    help = "Seed the permissions catalog and default roles."

    def handle(self, *args, **options):
        created_count = 0
        for module, actions in MODULE_PERMISSIONS.items():
            for action in actions:
                code = f"{module}.{action}"
                _, created = Permission.objects.get_or_create(
                    code=code,
                    defaults={
                        "module": module,
                        "action": action,
                        "description": f"Allows {action} on {module}.",
                    },
                )
                if created:
                    created_count += 1

        for code in RBAC_EXTRA_CODES:
            module, action = code.split(".", 1)
            _, created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    "module": module,
                    "action": action,
                    "description": f"Allows {action} operations.",
                },
            )
            if created:
                created_count += 1

        admin_role, _ = Role.objects.get_or_create(
            slug="admin",
            defaults={"name": "Admin", "description": "Platform administrator"},
        )
        customer_role, _ = Role.objects.get_or_create(
            slug="customer",
            defaults={"name": "Customer", "description": "Default customer role"},
        )

        all_permissions = Permission.objects.all()
        admin_role.permissions.set(all_permissions)

        customer_permissions = Permission.objects.filter(code__in=CUSTOMER_PERMISSION_CODES)
        customer_role.permissions.set(customer_permissions)

        self.stdout.write(self.style.SUCCESS(f"Permissions seeded (new: {created_count})."))
        self.stdout.write(self.style.SUCCESS("Default roles ensured: admin, customer."))
