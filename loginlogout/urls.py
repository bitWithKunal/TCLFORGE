"""
URL configuration for TCL Forge (loginlogout project).

Includes:
- Frontend pages (HTML)
- API endpoints (Auth, OTP, Reset, Profile)
- Static/Notes file serving (for PDFs, docs, etc.)
- Health-check endpoint
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
import os
import pymongo

# ✅ Import all API Views
from loginapp.views import (
    SignUpAPIView,
    LoginAPIView,
    LogoutAPIView,
    SendOTPAPIView,
    ResetPasswordAPIView,
    AuthenticatedResetPasswordView,
    ProfileAPIView,
)


# ===========================================================
# 🔹 FRONTEND + HEALTH CHECK VIEW
# ===========================================================
def home(request):
    """Default route and health-check endpoint"""
    if request.GET.get("api") == "true":
        try:
            client = pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=2000)
            client.server_info()
            db_status = "🟢 MongoDB Connected"
        except Exception as e:
            db_status = f"🔴 MongoDB Connection Error: {e}"

        return JsonResponse({
            "status": "✅ Django Server Running Successfully",
            "database": db_status,
            "project": "TCL Forge (loginlogout)",
        }, status=200)

    return render(request, "login.html")


# ===========================================================
# 🔹 FRONTEND VIEWS
# ===========================================================
def index_page(request):
    return render(request, "index.html")

def login_page(request):
    return render(request, "login.html")

def live_tcl_runner_page(request):
    return render(request, "live_tcl_runner.html")

def tcl_challenges_page(request):
    return render(request, "tcl_challenges.html")

def interview_prep_page(request):
    return render(request, "TCL_Interview_Pre.html")

def notes_page(request):
    return render(request, "notes.html")

def test_page(request):
    return render(request, "test.html")


# ===========================================================
# 🔹 FILE SERVING (e.g. /notes/TCL_Variables.pdf)
# ===========================================================
def serve_notes_file(request, filename):
    """Serve PDFs or files stored inside /templates/notes/"""
    notes_dir = os.path.join(settings.BASE_DIR, "loginlogout", "templates", "notes")
    file_path = os.path.join(notes_dir, filename)

    if os.path.exists(file_path):
        return FileResponse(open(file_path, "rb"), content_type="application/pdf")
    raise Http404("File not found")


# ===========================================================
# 🔹 URL PATTERNS
# ===========================================================
urlpatterns = [
    # Frontend Pages
    path("", home, name="frontend"),
    path("login.html", login_page, name="login_html"),
    path("index", index_page, name="index"),
    path("index.html", index_page, name="index_html"),
    path("live_tcl_runner.html", live_tcl_runner_page, name="live_tcl_runner"),
    path("tcl_challenges.html", tcl_challenges_page, name="tcl_challenges"),
    path("TCL_Interview_Pre.html", interview_prep_page, name="tcl_interview_pre"),
    path("notes.html", notes_page, name="notes"),
    path("test.html", test_page, name="test_page"),

    # 🔹 Serve PDFs inside /notes/
    path("notes/<str:filename>", serve_notes_file, name="serve_notes_file"),

    # Admin Panel
    path("admin/", admin.site.urls),

    # Auth APIs
    path("signup", SignUpAPIView.as_view(), name="signup"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("logout", LogoutAPIView.as_view(), name="logout"),

    # OTP / Reset APIs
    path("send-otp", SendOTPAPIView.as_view(), name="send_otp"),
    path("reset-password", ResetPasswordAPIView.as_view(), name="reset_password"),
    path("auth-reset-password", AuthenticatedResetPasswordView.as_view(), name="auth_reset_password"),

    # User Profile
    path("me", ProfileAPIView.as_view(), name="profile"),
]


# ===========================================================
# 🔹 MEDIA / STATIC SERVE (during development)
# ===========================================================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
