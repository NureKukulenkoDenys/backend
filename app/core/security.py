from typing import List
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.config import settings
from app.db.database import get_db
from app.db import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def create_access_token(data: dict):
    to_encode = data.copy()

    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    expire = datetime.utcnow() + timedelta(hours=12)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        return {
            "user_id": int(payload["sub"]),
            "role": payload["role"]
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )



def get_current_user_db(
    token_data=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = token_data["user_id"]
    role = token_data["role"]

    user = None

    if role == "administrator":
        user = db.query(models.Administrator).filter_by(id=user_id).first()
    elif role == "emergency_service":
        user = db.query(models.EmergencyService).filter_by(id=user_id).first()
    elif role == "business":
        user = db.query(models.BusinessUser).filter_by(id=user_id).first()

    if not user:
        raise HTTPException(401, "User not found")

    return {"user": user, "role": role}



def role_required(roles: List[str]):
    def wrapper(user_data=Depends(get_current_user_db)):
        if user_data["role"] not in roles:
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: insufficient role"
            )
        return user_data
    return wrapper
