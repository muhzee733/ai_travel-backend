from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from apps.rbac.models import Role, UserRole


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["role"] = user.role
        return token


class RegisterSerializer(serializers.ModelSerializer):
    # Explicit fields we want from client
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # username is optional; we'll auto-generate if not provided
        fields = ("id", "username", "email", "first_name", "last_name", "password")
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value):
        # extra safety: validate format + uniqueness
        try:
            django_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use.")

        return value

    def validate_password(self, value):
        # run through Django's global password validators
        try:
            validate_password(value)
        except DjangoValidationError as e:
            # e.messages is a list of human-readable errors
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data.pop("password")
        username = validated_data.get("username")

        # If username not provided, generate from email
        if not username:
            base_username = validated_data["email"].split("@")[0]
            candidate = base_username
            i = 1
            while User.objects.filter(username=candidate).exists():
                i += 1
                candidate = f"{base_username}{i}"
            username = candidate

        user = User(
            username=email,
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role="customer",  # all public registrations are customers
        )
        user.set_password(password)
        user.save()

        # Attach default customer role in RBAC
        try:
            customer_role = Role.objects.get(slug="customer")
            UserRole.objects.get_or_create(user=user, role=customer_role, defaults={"assigned_by": None})
        except Role.DoesNotExist:
            # Safe fallback if seed hasn't run yet
            pass
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 1) validate email format (same style as register)
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError({
                "email": "Invalid email format."
            })

        # 2) check if user exists
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "User not found."
            })

        # 3) check if active
        if not user.is_active:
            raise serializers.ValidationError({
                "email": "This account is disabled."
            })

        # 4) check password
        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "Incorrect password."
            })

        # 5) if you want to also ensure Django auth backend:
        # user = authenticate(username=user.username, password=password)
        # if not user:
        #     raise serializers.ValidationError({"password": "Incorrect password."})

        attrs["user"] = user
        return attrs


class MeSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "roles",
        ]
        read_only_fields = ["id", "username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get("instance")
        for optional_field in ["phone", "avatar_url"]:
            if user and hasattr(user, optional_field):
                self.fields[optional_field] = serializers.CharField(
                    required=False, allow_blank=True, allow_null=True
                )
                if optional_field not in self.Meta.fields:
                    self.Meta.fields.append(optional_field)

    def get_roles(self, obj):
        if hasattr(obj, "roles"):
            return list(obj.roles.values_list("slug", flat=True))
        return []

    def update(self, instance, validated_data):
        validated_data.pop("email", None)
        validated_data.pop("username", None)

        for field in ["first_name", "last_name", "phone", "avatar_url"]:
            if field in validated_data and hasattr(instance, field):
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")

        if not current_password or not user.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": ["Incorrect password."]}
            )

        if not new_password:
            raise serializers.ValidationError(
                {"new_password": ["This field may not be blank."]}
            )

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        attrs["user"] = user
        return attrs
