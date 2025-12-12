from pathlib import Path
from datetime import timedelta
import environ

# --------------------
# Paths
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------
# Environment setup
# --------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Read .env from project root (same folder as manage.py)
environ.Env.read_env(BASE_DIR / ".env")

# --------------------
# Security
# --------------------
# NEVER hard-code this in real projects – always from env
SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-secret-key-change-me"  # fallback for local only
)

DEBUG = env("DEBUG", default=True)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost"]
)

# --------------------
# Global user roles (optional but useful)
# --------------------
USER_ROLE_CHOICES = (
    ("admin", "Admin"),
    ("customer", "Customer"),
    # Add more later: ("hotel", "Hotel"), ("traveler", "Traveler")
)

# --------------------
# Application definition
# --------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",

    "apps.accounts",
    "apps.rbac",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --------------------
# Database (via DATABASE_URL)
# --------------------
# Example values for .env:
#   DATABASE_URL=sqlite:///db.sqlite3
#   DATABASE_URL=postgres://user:pass@host:5432/dbname
#   DATABASE_URL=mysql://user:pass@host:3306/dbname
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

# --------------------
# DRF & JWT
# --------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

ACCESS_TOKEN_LIFETIME_MINUTES = env.int(
    "ACCESS_TOKEN_LIFETIME_MINUTES",
    default=1440,  # 1 day
)
REFRESH_TOKEN_LIFETIME_DAYS = env.int(
    "REFRESH_TOKEN_LIFETIME_DAYS",
    default=7,
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS),
}

# --------------------
# CORS
# --------------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
)
CORS_ALLOW_CREDENTIALS = True

# --------------------
# Password validation
# --------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# --------------------
# Internationalization
# --------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------
# Static files
# --------------------
STATIC_URL = "static/"

# --------------------
# Default primary key field type
# --------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
