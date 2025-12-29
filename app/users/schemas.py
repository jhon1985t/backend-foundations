from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    full_name: str | None = Field(None, description="The user's full name")


class UserOut(UserCreate):
    id: int = Field(..., description="The user's unique identifier")

    model_config = {"from_attributes": True}
