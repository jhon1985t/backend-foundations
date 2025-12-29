from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import SessionLocal
from app.users.models import User
from app.users.schemas import UserOut, UserCreate
from app.exceptions import ConflictError


router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    # Check if user with the same email already exists
    existing_user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing_user:
        raise ConflictError(message="Email ya existe", details={"email": payload.email})

    new_user = User(email=payload.email, full_name=payload.full_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut(id=new_user.id, email=new_user.email, full_name=new_user.full_name)
