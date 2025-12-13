from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rbac", "0005_seed_roles_and_permissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="menu",
            name="slug",
            field=models.SlugField(default="sidebar_main", unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="menu",
            name="location",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="key",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="label",
            field=models.CharField(default="Item", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="menuitem",
            name="link_type",
            field=models.CharField(choices=[("INTERNAL", "Internal"), ("EXTERNAL", "External")], default="INTERNAL", max_length=20),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="path",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="menuitem",
            index=models.Index(fields=["menu", "parent", "sort_order"], name="rbac_menu_menu_id_61bfe2_idx"),
        ),
        migrations.RemoveField(
            model_name="menuitem",
            name="page_registry",
        ),
        migrations.RemoveField(
            model_name="menuitem",
            name="custom_label",
        ),
        migrations.RemoveField(
            model_name="menuitem",
            name="custom_path",
        ),
    ]
