from fastapi import APIRouter , HTTPException
from schemas.user_schema import UserCreate , UserLogin
from database import db
from utils.hashing import hash_password , verify_password
from utils.auth import create_token

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate):
    hashed_password = hash_password(user.password)

    await db.users.insert_one({
        "email": user.email,
        "password": hashed_password
    })

    return {"msg": "User created"}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_token({"email": user.email})

    return {"access_token": token}