from fastapi import APIRouter , HTTPException, Depends, status
from schemas.user_schema import UserCreate , UserLogin
from database import db
from utils.hashing import hash_password , verify_password
from utils.auth import create_token, verify_token, verify_role
from utils.Constants.app_constants import ERROR_MESSAGES, SUCCESS_MESSAGES, VALID_ROLES
from Exceptions.decorators import (
    handle_auth_exceptions,
    handle_admin_exceptions,
    handle_db_exceptions,
    handle_exceptions
)

router = APIRouter()

@router.post("/signup")
@handle_auth_exceptions
async def signup(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail=ERROR_MESSAGES["email_exists"])
    
    hashed_password = hash_password(user.password)

    await db.users.insert_one({
        "email": user.email,
        "password": hashed_password,
        "role": user.role
    })

    return {"msg": SUCCESS_MESSAGES["user_created"], "role": user.role}

@router.post("/login")
@handle_auth_exceptions
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail=ERROR_MESSAGES["invalid_password"])

    token = create_token({"email": user.email, "role": db_user.get("role", "user")})

    return {"access_token": token}

@router.get("/protected")
@handle_exceptions
async def protected_route(user=Depends(verify_token)):
    return {"msg": "Authorized", "user_email": user.get("email"), "role": user.get("role")}

# ===================== ADMIN ENDPOINTS =====================

@router.get("/admin/all-users")
@handle_admin_exceptions
@handle_db_exceptions
async def get_all_users(admin_user=Depends(verify_role(["admin"]))):
    """Admin only: Get all users in the system"""
    users = []
    async for user in db.users.find({}, {"password": 0}):  # Exclude passwords
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@router.delete("/admin/delete-user/{email}")
@handle_admin_exceptions
@handle_db_exceptions
async def delete_user(email: str, admin_user=Depends(verify_role(["admin"]))):
    """Admin only: Delete a user by email"""
    result = await db.users.delete_one({"email": email})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    return {"msg": f"User {email} {SUCCESS_MESSAGES['user_deleted'].lower()}"}

@router.put("/admin/update-user-role/{email}")
@handle_admin_exceptions
@handle_db_exceptions
async def update_user_role(
    email: str, 
    new_role: str,
    admin_user=Depends(verify_role(["admin"]))
):
    """Admin only: Update user role"""
    if new_role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")
    
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"role": new_role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["user_not_found"])
    
    return {"msg": f"User {email} {SUCCESS_MESSAGES['role_updated'].lower()} to {new_role}"}