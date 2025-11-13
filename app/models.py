from pydantic import BaseModel, Field, PositiveFloat


class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, description="The name of the item")
    price: PositiveFloat = Field(
        ..., description="The price of the item, must be positive"
    )
    description: str | None = Field(None, description="A brief description of the item")


class ItemOut(ItemIn):
    id: int = Field(..., description="The unique identifier of the item")
