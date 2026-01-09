import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.cache import get_redis
from app.exceptions import ResourceNotFound
from app.dependencies import get_db
from app.users.models import User
from app.users.schemas import UserOut, UserCreate
from app.exceptions import ConflictError
from app.kafka.producer import emit_user_created
from app.auth.security import hash_password
from app.auth.deps import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    # Check if user with the same email already exists
    existing_user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing_user:
        raise ConflictError(message="Email ya existe", details={"email": payload.email})

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Emit Kafka event
    emit_user_created(user_id=new_user.id, email=new_user.email)

    return UserOut(id=new_user.id, email=new_user.email, full_name=new_user.full_name)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(
        id=current_user.id, email=current_user.email, full_name=current_user.full_name
    )


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserOut:
    redis = await get_redis()
    cache_key = f"user:{user_id}"
    # Try to get user data from Redis cache
    cached_user = await redis.get(cache_key)
    if cached_user:
        user_data = json.loads(cached_user)
        return UserOut(**user_data)

    # If not in cache, fetch from database
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise ResourceNotFound(
            message="Usuario no encontrado", details={"user_id": user_id}
        )

    user_out = UserOut(id=user.id, email=user.email, full_name=user.full_name)
    # Store user data in Redis cache
    await redis.set(cache_key, user_out.model_dump_json())
    return user_out
