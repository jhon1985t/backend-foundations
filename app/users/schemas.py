from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    full_name: str | None = Field(None, description="The user's full name")
    password: str = Field(..., description="The user's password")


class UserOut(BaseModel):
    id: int = Field(..., description="The user's unique identifier")
    email: EmailStr = Field(..., description="The user's email address")
    full_name: str | None = Field(None, description="The user's full name")

    model_config = {"from_attributes": True}
