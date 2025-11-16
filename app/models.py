from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    field_validator,
    model_validator,
)
import re

SKU_RE = re.compile(r"^[A-Z0-9-]{6,20}$")


class ItemIn(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=80, description="The name of the item"
    )
    price: PositiveFloat = Field(
        ..., description="The price of the item, must be positive"
    )
    discount: float = Field(
        0.0, ge=0.0, le=0.9, description="The discount percentage on the item"
    )
    sku: str | None = Field(None, description="The Stock Keeping Unit identifier")
    description: str | None = Field(None, description="A brief description of the item")

    @field_validator("name")
    @classmethod
    def strip_and_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be empty or whitespace")
        return v

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v: str) -> str:
        if v is None:
            return v
        if not SKU_RE.match(v):
            raise ValueError(
                "SKU must be 6-20 characters long, uppercase letters, digits and hyphens only"
            )
        return v

    @model_validator(mode="after")
    def check_business_rules(self):
        final_price = self.price * (1 - self.discount)
        if final_price < 1.0:
            raise ValueError("Final price after discount must be at least 1.0")
        return self


class ItemOut(ItemIn):
    id: int = Field(..., description="The unique identifier of the item")
