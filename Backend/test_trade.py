import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from models import OrderCreate
from routes.trading import trade

# Mock order data
mock_order = OrderCreate(
    symbol="BTC",
    quantity=2,
    price=300.0,
    total_price=600.0
)

@pytest.mark.asyncio
async def test_trade_successful():
    """Test a successful trade execution"""

    # Patch Portfolio.get_or_create and Transaction
    with patch('routes.trading.Portfolio.get_or_create', new_callable=AsyncMock) as mock_get_or_create, \
         patch('routes.trading.Transaction') as mock_transaction_class:

        # Mock portfolio instance
        mock_portfolio_instance = AsyncMock()
        mock_portfolio_instance.symbol = "BTC"
        mock_portfolio_instance.quantity = 0
        mock_get_or_create.return_value = mock_portfolio_instance

        # Mock transaction instance
        mock_transaction_instance = MagicMock()
        mock_transaction_instance.insert = AsyncMock()
        mock_transaction_class.return_value = mock_transaction_instance

        # Mock user
        mock_user = MagicMock()
        mock_user.id = 'test_user_123'
        mock_user.credit = 1000.0
        mock_user.username = 'testuser'
        mock_user.save = AsyncMock()

        # Execute trade
        result = await trade(mock_order, mock_user)

# Use dot notation for Pydantic model
        assert result.message == "Trade executed successfully"
        assert result.symbol == mock_order.symbol
        assert result.quantity == mock_order.quantity
        assert result.remaining_credits == 1000.0 - mock_order.total_price
        # Verify mocks were called
        mock_portfolio_instance.save.assert_awaited_once()
        mock_transaction_instance.insert.assert_awaited_once()
        mock_user.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_trade_insufficient_credits():
    """Test trade fails when user has insufficient credits"""

    # Mock user with low credits
    poor_user = MagicMock()
    poor_user.id = 'poor_user'
    poor_user.credit = 100.0
    poor_user.username = 'pooruser'
    poor_user.save = AsyncMock()

    expensive_order = OrderCreate(
        symbol="BTC",
        quantity=1,
        price=500.0,
        total_price=500.0
    )

    # Patch Portfolio.get_or_create to avoid DB access
    with patch('routes.trading.Portfolio.get_or_create', new_callable=AsyncMock) as mock_get_or_create:
        mock_portfolio_instance = AsyncMock()
        mock_portfolio_instance.symbol = "BTC"
        mock_portfolio_instance.quantity = 0
        mock_get_or_create.return_value = mock_portfolio_instance

        # Execute trade and expect HTTPException
        with pytest.raises(HTTPException) as exc:
            await trade(expensive_order, poor_user)

        assert exc.value.status_code == 400
        assert "Insufficient credits" in exc.value.detail
        poor_user.save.assert_not_awaited()
