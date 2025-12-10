import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from bson import ObjectId

User = get_user_model()


# =====================================================
# 🔹 SIGNUP API
# =====================================================
class SignUpAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if not email or not username or not password:
            return Response({"error": "All fields are required"}, status=400)

        # Check if email already exists
        if settings.LOGIN_COLLECTION.find_one({"email": email}):
            return Response({"error": "Email already exists"}, status=400)

        hashed_password = make_password(password)

        user_data = {
            "_id": str(ObjectId()),
            "email": email,
            "username": username,
            "password": hashed_password,
            "created_at": timezone.now(),
        }
        settings.LOGIN_COLLECTION.insert_one(user_data)
        return Response({"message": "Signup successful"}, status=201)


# =====================================================
# 🔹 LOGIN API
# =====================================================
class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        user = settings.LOGIN_COLLECTION.find_one({"email": email})
        if not user or not check_password(password, user["password"]):
            return Response({"error": "Invalid credentials"}, status=401)

        # ✅ Proper JWT generation with embedded email
        refresh = RefreshToken()
        refresh["email"] = email  # embed email for token-based auth

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": email
        }, status=200)


# =====================================================
# 🔹 LOGOUT API
# =====================================================
class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"error": "Invalid or expired token"}, status=400)

        return Response({"message": "Logout successful"}, status=200)


# =====================================================
# 🔹 SEND OTP FOR PASSWORD RESET
# =====================================================

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = settings.LOGIN_COLLECTION.find_one({"email": email})
        if not user:
            return Response({"error": "User not found"}, status=404)

        last_otp = settings.RESET_OTP_COLLECTION.find_one(
            {"email": email}, sort=[("created_at", -1)]
        )
        if last_otp:
            otp_created_at = last_otp["created_at"]
            if otp_created_at.tzinfo is None:
                otp_created_at = timezone.make_aware(otp_created_at)
            if (timezone.now() - otp_created_at).total_seconds() < 60:
                return Response(
                    {"error": "Wait 60 seconds before requesting another OTP"},
                    status=429
                )

        otp = str(random.randint(100000, 999999))
        settings.RESET_OTP_COLLECTION.insert_one({
            "email": email,
            "otp": otp,
            "created_at": timezone.now(),
            "is_used": False
        })

        try:
            send_mail(
                subject = "TCL Forge Password Assistance - OTP Verification",
                message = (
    "TCL Forge Password Reset\n\n"
    "Dear User,\n\n"
    f"Your OTP for password reset is: {otp}\n\n"
    "This code will expire in 5 minutes.\n"
    "If you did not request this reset, please ignore this message.\n\n"
    "— TCL Forge\n"
    "Tool created by Kunal Saraswat"
)


            from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {e}"}, status=500)

        return Response({"message": "OTP sent successfully to your email."}, status=200)


# =====================================================
# 🔹 RESET PASSWORD VIA OTP
# =====================================================
class ResetPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("password")

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP and new password are required"}, status=400)

        otp_doc = settings.RESET_OTP_COLLECTION.find_one(
            {"email": email, "otp": otp, "is_used": False},
            sort=[("created_at", -1)]
        )
        if not otp_doc:
            return Response({"error": "Invalid OTP"}, status=400)

        otp_created_at = otp_doc["created_at"]
        if otp_created_at.tzinfo is None:
            otp_created_at = timezone.make_aware(otp_created_at)
        if (timezone.now() - otp_created_at).total_seconds() > 300:
            return Response({"error": "OTP expired"}, status=400)

        settings.RESET_OTP_COLLECTION.update_one(
            {"_id": otp_doc["_id"]}, {"$set": {"is_used": True}}
        )

        user_doc = settings.LOGIN_COLLECTION.find_one({"email": email})
        if not user_doc:
            return Response({"error": "User not found"}, status=404)

        if check_password(new_password, user_doc["password"]):
            return Response({"error": "Cannot reuse old password"}, status=400)

        hashed_new = make_password(new_password)
        settings.LOGIN_COLLECTION.update_one(
            {"email": email}, {"$set": {"password": hashed_new}}
        )

        return Response({"message": "Password reset successful"}, status=200)


# =====================================================
# 🔹 RESET PASSWORD (Logged-in user, JWT)
# =====================================================
class AuthenticatedResetPasswordView(APIView):
    """Allows logged-in users to reset password using JWT"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            jwt_auth = JWTAuthentication()
            header = jwt_auth.get_header(request)
            raw_token = jwt_auth.get_raw_token(header)
            validated_token = jwt_auth.get_validated_token(raw_token)
            email = validated_token.get("email")

            if not email:
                return Response({"error": "Invalid or missing email in token"}, status=401)

            old_password = request.data.get("old_password")
            new_password = request.data.get("new_password")

            if not old_password or not new_password:
                return Response({"error": "Both old and new passwords are required"}, status=400)

            user_doc = settings.LOGIN_COLLECTION.find_one({"email": email})
            if not user_doc:
                return Response({"error": "User not found"}, status=404)

            if not check_password(old_password, user_doc["password"]):
                return Response({"error": "Incorrect current password"}, status=400)

            if check_password(new_password, user_doc["password"]):
                return Response({"error": "New password cannot be same as old password"}, status=400)

            hashed_new = make_password(new_password)
            settings.LOGIN_COLLECTION.update_one(
                {"email": email}, {"$set": {"password": hashed_new}}
            )

            return Response({"message": "Password updated successfully"}, status=200)

        except Exception as e:
            return Response({"error": f"Token validation failed: {str(e)}"}, status=401)


# =====================================================
# 🔹 USER PROFILE API (Fetch logged-in user info)
# =====================================================
class ProfileAPIView(APIView):
    """Returns profile info of the logged-in user (requires JWT token)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            jwt_auth = JWTAuthentication()
            header = jwt_auth.get_header(request)
            raw_token = jwt_auth.get_raw_token(header)
            validated_token = jwt_auth.get_validated_token(raw_token)
            email = validated_token.get("email")

            if not email:
                return Response({"error": "Invalid token or email missing"}, status=401)

            user = settings.LOGIN_COLLECTION.find_one({"email": email})
            if not user:
                return Response({"error": "User not found"}, status=404)

            return Response({
                "username": user.get("username"),
                "email": user.get("email"),
                "created_at": (
                    user.get("created_at").strftime("%Y-%m-%d %H:%M:%S")
                    if user.get("created_at") else None
                )
            }, status=200)
        except Exception as e:
            return Response({"error": f"Profile fetch failed: {str(e)}"}, status=401)
