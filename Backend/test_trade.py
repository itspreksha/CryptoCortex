import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from models import OrderCreate
from routes.trading import trade

# Mock user data
mock_user = type('MockUser', (), {
    'id': 'test_user_123',
    'credit': 1000.0,
    'username': 'testuser'
})()

# Mock order data
mock_order = OrderCreate(
    symbol="BTC",
    quantity=2.0,
    price=300.0,
    total_price=600.0
)

@pytest.mark.asyncio
async def test_trade_successful():
    """Test successful trade"""
    with patch('routes.trading.Portfolio.get_or_create') as mock_portfolio:
        with patch('routes.trading.Transaction') as mock_transaction:
            
            # Setup mocks
            mock_portfolio.return_value = AsyncMock(quantity=0)
            mock_transaction.return_value = AsyncMock()
            
            # Execute trade
            result = await trade(mock_order, mock_user)
            
            # Verify results
            assert result["message"] == "Trade executed"
            mock_portfolio.return_value.save.assert_called_once()
            mock_transaction.return_value.insert.assert_called_once()

@pytest.mark.asyncio
async def test_trade_insufficient_credits():
    """Test trade with insufficient credits"""
    poor_user = type('MockUser', (), {
        'id': 'poor_user',
        'credit': 100.0,
        'username': 'pooruser'
    })()
    
    expensive_order = OrderCreate(
        symbol="BTC",
        quantity=1.0,
        price=500.0,
        total_price=500.0
    )
    
    # Should raise error
    with pytest.raises(HTTPException) as exc:
        await trade(expensive_order, poor_user)
    
    assert exc.value.status_code == 400
    assert "Insufficient credits" in exc.value.detail