from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("rbac", "0002_permission_deleted_at_permission_is_deleted_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageRegistry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("key", models.CharField(max_length=150, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("path", models.CharField(max_length=255)),
                ("default_icon", models.CharField(max_length=100)),
                ("permission", models.JSONField(blank=True, null=True)),
                ("type", models.CharField(choices=[("SYSTEM", "System"), ("CMS", "CMS"), ("CUSTOM_LINK", "Custom Link")], default="SYSTEM", max_length=20)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="Menu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=150)),
                ("location", models.CharField(max_length=150, unique=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={
                "ordering": ("location",),
            },
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("custom_label", models.CharField(blank=True, max_length=200, null=True)),
                ("custom_path", models.CharField(blank=True, max_length=255, null=True)),
                ("icon", models.CharField(blank=True, max_length=100, null=True)),
                ("permission", models.JSONField(blank=True, null=True)),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=1)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("menu", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="items", to="rbac.menu")),
                ("page_registry", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="menu_items", to="rbac.pageregistry")),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name="children", to="rbac.menuitem")),
            ],
            options={
                "ordering": ("sort_order", "id"),
            },
        ),
    ]
