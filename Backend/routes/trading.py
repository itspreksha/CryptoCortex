from fastapi import APIRouter, Depends, HTTPException
from models import OrderCreate, Transaction, Portfolio
from .token import get_current_user   
from models import User             

router = APIRouter()

@router.post("/trade")
async def trade(order: OrderCreate, user: User = Depends(get_current_user)):
    

    if user.credit < order.total_price:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    portfolio = await Portfolio.get_or_create(user.id, order.symbol)
    portfolio.quantity += order.quantity
    await portfolio.save()

    transaction = Transaction(
        user_id=user.id,
        symbol=order.symbol,
        quantity=order.quantity
    )
    await transaction.insert()
    
    return {"message": "Trade executed"}
