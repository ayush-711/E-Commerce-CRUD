"""
Application Configuration & Constants
All app-related constants should be defined here
"""

from datetime import timedelta

# ===================== JWT Configuration =====================
SECRET_KEY = "mysecretkey"  # TODO: Move to .env file for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

# ===================== Token Expiry Settings =====================
TOKEN_EXPIRY = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

# ===================== Role Constants =====================
VALID_ROLES = ["admin", "user", "supplier"]
ROLE_ADMIN = "admin"
ROLE_USER = "user"
ROLE_SUPPLIER = "supplier"

# ===================== HTTP Status Codes =====================
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500

# ===================== Error Messages =====================
ERROR_MESSAGES = {
    "token_expired": "Token expired",
    "invalid_token": "Invalid token",
    "access_denied": "Access denied",
    "user_not_found": "User not found",
    "invalid_password": "Invalid password",
    "email_exists": "Email already registered",
    "email_required": "Email is required",
    "password_required": "Password is required",
    "product_not_found": "Product not found",
    "insufficient_permissions": "Insufficient permissions",
}

# ===================== Success Messages =====================
SUCCESS_MESSAGES = {
    "user_created": "User created",
    "product_added": "Product added",
    "product_updated": "Product updated",
    "product_deleted": "Product deleted",
    "user_deleted": "User deleted",
    "role_updated": "Role updated",
}
