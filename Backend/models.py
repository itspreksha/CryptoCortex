from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class OrderCreate(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    quantity: float = Field(..., gt=0, example=1.5)
    total_price: float = Field(..., gt=0, example=100.0)

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str 
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(Document):
    username: str = Field(..., description="Unique username")
    password_hash: str
    credit: float =Field(default=100.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users" 

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "testuser",
                "hashed_password": "hashedpassword123"
            }
        }

class Transaction(Document):
    user_id: PydanticObjectId = Field(...)
    symbol: str = Field(...)
    quantity: float = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "transactions"   


class Portfolio(Document):
    user_id: PydanticObjectId = Field(...)
    symbol: str = Field(...)
    quantity: float = Field(default=0.0)


    class Settings:
        name = "portfolios"   # MongoDB collection name

    @classmethod
    async def get_or_create(cls, user_id: str, symbol: str):
        portfolio = await cls.find_one({"user_id": user_id, "symbol": symbol})
        if not portfolio:
            portfolio = cls(user_id=user_id, symbol=symbol, quantity=0.0)
            await portfolio.insert()
        return portfolio

