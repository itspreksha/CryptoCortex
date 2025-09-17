from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderCreate, Transaction, Portfolio, User
from .token import get_current_user
from pydantic import BaseModel

router = APIRouter()


class TradeResponse(BaseModel):
    message: str
    symbol: str
    quantity: int
    remaining_credits: float


async def execute_trade(order: OrderCreate, user: User):
    """Handles trade execution logic."""

    # Check balance
    if user.credit < order.total_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient credits"
        )

    # Update portfolio
    portfolio = await Portfolio.get_or_create(user.id, order.symbol)
    portfolio.quantity += order.quantity
    await portfolio.save()

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        symbol=order.symbol,
        quantity=order.quantity
    )
    await transaction.insert()

    # Deduct credits
    user.credit -= order.total_price
    await user.save()

    return portfolio, user


@router.post("/trade", response_model=TradeResponse)
async def trade(order: OrderCreate, user: User = Depends(get_current_user)):
    """Endpoint for executing a trade."""

    portfolio, updated_user = await execute_trade(order, user)

    return TradeResponse(
        message="Trade executed successfully",
        symbol=portfolio.symbol,
        quantity=order.quantity,
        remaining_credits=updated_user.credit
    )
    