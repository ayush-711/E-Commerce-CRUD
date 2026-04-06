from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.Constants.app_constants import SECRET_KEY, ALGORITHM, TOKEN_EXPIRY, ERROR_MESSAGES

def create_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + TOKEN_EXPIRY
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES["token_expired"])
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES["invalid_token"])

def verify_role(required_roles: list):
    """
    Dependency to verify user has required role.
    Usage: @router.get("/admin-only", dependencies=[Depends(verify_role(["admin"]))])
    Or: user=Depends(verify_role(["admin", "supplier"]))
    """
    async def check_role(user: dict = Depends(verify_token)):
        user_role = user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{ERROR_MESSAGES['access_denied']}. Required roles: {', '.join(required_roles)}"
            )
        return user
    
    return check_role