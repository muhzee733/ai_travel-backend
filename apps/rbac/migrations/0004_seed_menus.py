from django.db import migrations


def seed_menu(apps, schema_editor):
    PageRegistry = apps.get_model("rbac", "PageRegistry")
    Menu = apps.get_model("rbac", "Menu")
    MenuItem = apps.get_model("rbac", "MenuItem")

    default_pages = [
        ("dashboard", "Dashboard", "/dashboard", "Home", None, "SYSTEM"),
        ("settings", "Settings", "/settings", "Settings", ["settings.view", "settings.manage"], "SYSTEM"),
        ("reports", "Reports", "/reports", "BarChart3", "reports.view", "SYSTEM"),
        ("hotels", "Hotels", "/hotels", "Building2", "hotels.view", "SYSTEM"),
        ("cars", "Cars", "/cars", "Car", "cars.view", "SYSTEM"),
        ("airtickets", "AirTickets", "/airtickets", "Plane", "airtickets.view", "SYSTEM"),
        ("visa", "Visa", "/visa", "BadgeCheck", "visa.view", "SYSTEM"),
        ("admin-menu", "Menu Builder", "/admin/menus", "Settings", ["settings.manage", "rbac.manage_roles"], "SYSTEM"),
    ]

    for idx, (key, title, path, icon, perm, typ) in enumerate(default_pages, start=1):
        PageRegistry.objects.update_or_create(
            key=key,
            defaults={
                "title": title,
                "path": path,
                "default_icon": icon,
                "permission": perm,
                "type": typ,
                "is_active": True,
            },
        )

    sidebar, _ = Menu.objects.get_or_create(
        location="sidebar",
        defaults={"name": "Sidebar", "is_active": True},
    )

    # Seed menu items in order
    for idx, (key, _, _, _, _, _) in enumerate(default_pages, start=1):
        page = PageRegistry.objects.filter(key=key).first()
        if page:
            MenuItem.objects.update_or_create(
                menu=sidebar,
                page_registry=page,
                parent=None,
                defaults={
                    "custom_label": None,
                    "custom_path": None,
                    "icon": None,
                    "permission": None,
                    "sort_order": idx,
                    "is_active": True,
                },
            )


def unseed_menu(apps, schema_editor):
    PageRegistry = apps.get_model("rbac", "PageRegistry")
    Menu = apps.get_model("rbac", "Menu")
    MenuItem = apps.get_model("rbac", "MenuItem")
    keys = [
        "dashboard",
        "settings",
        "reports",
        "hotels",
        "cars",
        "airtickets",
        "visa",
        "admin-menu",
    ]
    MenuItem.objects.filter(page_registry__key__in=keys).delete()
    PageRegistry.objects.filter(key__in=keys).delete()
    Menu.objects.filter(location="sidebar").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0003_menubuilder"),
    ]

    operations = [
        migrations.RunPython(seed_menu, reverse_code=unseed_menu),
    ]
