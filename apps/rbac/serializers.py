from django.contrib.auth import get_user_model
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Permission, Role, MenuItem, PageRegistry, Menu


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id",
            "code",
            "module",
            "action",
            "description",
            "created_at",
            "updated_at",
        ]


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "permissions",
            "created_at",
            "updated_at",
        ]

    def get_permissions(self, obj):
        return list(obj.permissions.values_list("code", flat=True))


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        validators=[UniqueValidator(queryset=Role.objects.all(), message="Slug must be unique.")],
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]

    def validate_slug(self, value):
        normalized = slugify(value) or value
        qs = Role.objects.filter(slug__iexact=normalized)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Slug must be unique.")
        return normalized


class UserBasicSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "roles",
        ]

    def get_roles(self, obj):
        return list(obj.roles.values_list("slug", flat=True))


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "menu",
            "parent",
            "key",
            "label",
            "link_type",
            "path",
            "url",
            "icon",
            "permission",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        link_type = attrs.get("link_type", MenuItem.LinkTypes.INTERNAL)
        path = attrs.get("path")
        url = attrs.get("url")
        parent = attrs.get("parent")

        if link_type == MenuItem.LinkTypes.INTERNAL:
            if not path or not path.startswith("/"):
                raise serializers.ValidationError({"path": "Internal links must start with '/'."})
            attrs["url"] = None
        else:
            if not url:
                raise serializers.ValidationError({"url": "External links require a URL."})
            attrs["path"] = None

        # permission validation
        perm = attrs.get("permission")
        if perm is not None and not isinstance(perm, (str, list, tuple)):
            raise serializers.ValidationError({"permission": "Permission must be null, string, or array."})
        if isinstance(perm, (list, tuple)):
            for p in perm:
                if not isinstance(p, str):
                    raise serializers.ValidationError({"permission": "Permission array must contain strings."})

        if parent and parent.parent:
            raise serializers.ValidationError({"parent": "Only two levels are allowed (parent + child)."})
        return attrs


class MenuItemReorderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=False,
    )

    def validate_order(self, value):
        ids = [item.get("id") for item in value]
        if any(v is None for v in ids):
            raise serializers.ValidationError("Each item must include an id.")
        return value


class PageRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRegistry
        fields = [
            "id",
            "key",
            "title",
            "path",
            "default_icon",
            "permission",
            "type",
            "is_active",
        ]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "name", "slug", "location", "is_active", "created_at", "updated_at"]
