

from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol or len(symbol) < 3:
        raise ValidationError(f"Invalid symbol: '{symbol}'. Example: BTCUSDT")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side: '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type: '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got: {quantity}")
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    if order_type in {"LIMIT", "STOP"}:
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        if price <= 0:
            raise ValidationError(f"Price must be greater than 0, got: {price}")
    return price


def validate_stop_price(stop_price: Optional[float], order_type: str) -> Optional[float]:
    if order_type in {"STOP", "STOP_MARKET"}:
        if stop_price is None:
            raise ValidationError(f"Stop price is required for {order_type} orders.")
        if stop_price <= 0:
            raise ValidationError(f"Stop price must be greater than 0, got: {stop_price}")
    return stop_price


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type.upper()),
        "stop_price": validate_stop_price(stop_price, order_type.upper()),
    }
