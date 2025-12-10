from dotenv import load_dotenv
import os
import pymongo
from pathlib import Path
from datetime import timedelta

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve().parent.parent  # points to ...\login\loginlogout

# === CORRECT .ENV FILE PATH ===
# (your .env file lives here: ...\login\loginlogout\.env)
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

# === LOG INFO ONCE ===
if os.environ.get('RUN_MAIN') != 'true':
    print(f"✅ .env loaded from: {ENV_PATH} (exists={ENV_PATH.exists()})")

# === DJANGO CORE SETTINGS ===
SECRET_KEY = 'django-insecure-#%^m(!7e)((2^ew5je+ah8#!$)vjoq_f1*_r)e8dgx%c1xjwzr'
DEBUG = True
ALLOWED_HOSTS = ["*"]

# === INSTALLED APPS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'loginapp',
    'rest_framework_simplejwt',
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",  # ✅ for frontend (CORS)
]

# === REST FRAMEWORK CONFIG ===
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_USER_MODEL = 'loginapp.User'

# === EMAIL SETTINGS ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'kunalsaraswat30@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

if not EMAIL_HOST_PASSWORD:
    print("⚠️ Warning: EMAIL_PASSWORD not found in .env file.")

# === AUTHENTICATION BACKENDS ===
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ✅ must be before CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === URL & TEMPLATES CONFIG ===
ROOT_URLCONF = 'loginlogout.urls'

# ✅ FIXED TEMPLATE DIRECTORY
# (Your actual path: login\loginlogout\loginlogout\templates\login.html)
TEMPLATE_DIR = BASE_DIR / "loginlogout" / "templates"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],  # ✅ Django can now find login.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'loginlogout.wsgi.application'

# === DATABASE (SQLite) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# === MONGODB CONFIG ===
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "TCL_Forge")

if not MONGO_URI:
    print("⚠️ Warning: MONGO_URI not found in .env file.")

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client[DB_NAME]
    client.server_info()  # test connection
    print("🟢 MongoDB connected successfully.")
except Exception as e:
    print(f"🔴 MongoDB connection failed: {e}")
    db = None

# === COLLECTIONS ===
if db is not None:
    LOGIN_COLLECTION = db["Login"]
    RESET_OTP_COLLECTION = db["password_reset_otp"]

# === PASSWORD VALIDATORS ===
AUTH_PASSWORD_VALIDATORS = []  # disabled for simplicity

# === LANGUAGE / TIMEZONE / STATIC ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === SIMPLE JWT CONFIG ===
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# === CORS SETTINGS ===
CORS_ALLOW_ALL_ORIGINS = True  # ✅ allow requests from your local frontend
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
]

# === FINAL CONFIRMATION ===
if os.environ.get('RUN_MAIN') != 'true':
    print(f"✅ Templates Path: {TEMPLATE_DIR}")
    print("✅ Django settings configured successfully.")
