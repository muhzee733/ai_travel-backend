from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Permission, Role


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
    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


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
