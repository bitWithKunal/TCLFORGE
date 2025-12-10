import os
import sys
import subprocess

# === 1️⃣ AUTO-INSTALL REQUIRED DEPENDENCIES ===
required_modules = [
    "django",
    "djangorestframework",
    "djangorestframework-simplejwt",
    "django-cors-headers",
]

print("🔧 Checking and installing required packages...\n")
for module in required_modules:
    try:
        __import__(module.split("-")[0])
    except ImportError:
        print(f"📦 Installing missing module: {module}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

# === 2️⃣ PROJECT PATH ===
project_path = os.path.join(os.path.dirname(__file__), "loginlogout")

if not os.path.exists(project_path):
    raise FileNotFoundError(f"❌ Project path not found: {project_path}")

os.chdir(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loginlogout.settings")

# === 3️⃣ START SERVER ===
try:
    import django
    from django.core.management import execute_from_command_line

    django.setup()
    print("\n🚀 Starting Django server at http://127.0.0.1:8000/\n")
    execute_from_command_line(["manage.py", "runserver"])
except Exception as e:
    print("❌ Error while running Django server:\n", e)
