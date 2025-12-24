from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt

from app.db.database import get_db
from app.db.models import Administrator, EmergencyService, BusinessUser
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username
    password = form_data.password.encode("utf-8")

    admin = db.query(Administrator).filter(Administrator.email == email).first()
    if admin:
        if bcrypt.checkpw(password, admin.password.encode("utf-8")):
            token = create_access_token({"sub": admin.id, "role": "administrator"})
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": "administrator"
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")

    service = db.query(EmergencyService).filter(EmergencyService.email == email).first()
    if service:
        if bcrypt.checkpw(password, service.password.encode("utf-8")):
            token = create_access_token({"sub": service.id, "role": "emergency_service"})
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": "emergency_service"
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")

    business = db.query(BusinessUser).filter(BusinessUser.email == email).first()
    if business:
        if bcrypt.checkpw(password, business.password.encode("utf-8")):
            token = create_access_token({"sub": business.id, "role": "business"})
            return {
                "access_token": token,
                "token_type": "bearer",
                "role": "business"
            }
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")

 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )


@router.post(
    "/business/register",
    status_code=status.HTTP_201_CREATED
)
def register_business(
    email: str,
    password: str,
    business_name: str,
    db: Session = Depends(get_db)
):
 
    existing_business = (
        db.query(BusinessUser)
        .filter(BusinessUser.email == email)
        .first()
    )

    if existing_business:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business user with this email already exists"
        )

   
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    
    new_business = BusinessUser(
        email=email,
        password=hashed_password,
        business_name=business_name
    )

    db.add(new_business)
    db.commit()
    db.refresh(new_business)

  
    token = create_access_token({
        "sub": new_business.id,
        "role": "business"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "business"
    }

