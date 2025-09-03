from pydantic import BaseModel, conint
from typing import List

class ProductBase(BaseModel):
    name: str
    price: float
    stock: int

class ProductOut(ProductBase):
    id: int
    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: conint(gt=0)

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    items: List[OrderItemOut]
    created_at: str
    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    email: str
    class Config:
        orm_mode = True
