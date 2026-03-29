from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")