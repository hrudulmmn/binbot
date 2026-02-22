
from typing import Optional

from binance.exceptions import BinanceAPIException, BinanceRequestException

from client import BinanceClientWrapper
from logging_config import setup_logger
from validators import validate_order_params

logger = setup_logger("trading_bot.orders")


def _build_order_summary(params: dict) -> str:
    lines = [
        "┌─ Order Request ──────────────────────────────",
        f"│  Symbol     : {params['symbol']}",
        f"│  Side       : {params['side']}",
        f"│  Type       : {params['order_type']}",
        f"│  Quantity   : {params['quantity']}",
    ]
    if params.get("price"):
        lines.append(f"│  Price      : {params['price']}")
    if params.get("stop_price"):
        lines.append(f"│  Stop Price : {params['stop_price']}")
    lines.append("└──────────────────────────────────────────────")
    return "\n".join(lines)


def _build_order_result(response: dict) -> str:
    lines = [
        "┌─ Order Response ─────────────────────────────",
        f"│  Order ID   : {response.get('orderId')}",
        f"│  Status     : {response.get('status')}",
        f"│  Symbol     : {response.get('symbol')}",
        f"│  Side       : {response.get('side')}",
        f"│  Type       : {response.get('type')}",
        f"│  Orig Qty   : {response.get('origQty')}",
        f"│  Exec Qty   : {response.get('executedQty')}",
        f"│  Avg Price  : {response.get('avgPrice') or response.get('price') or 'N/A'}",
        "└──────────────────────────────────────────────",
    ]
    return "\n".join(lines)


def place_order(
    client: BinanceClientWrapper,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )

    summary = _build_order_summary(params)
    print(summary)
    logger.info("Order request validated:\n%s", summary)

    try:
        response = client.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params.get("price"),
            stop_price=params.get("stop_price"),
        )
    except BinanceAPIException as exc:
        logger.error("BinanceAPIException [%s]: %s", exc.code, exc.message)
        print(f"\n Order FAILED — Binance error [{exc.code}]: {exc.message}")
        raise
    except BinanceRequestException as exc:
        logger.error("BinanceRequestException: %s", exc.message)
        print(f"\n Order FAILED — Network/request error: {exc.message}")
        raise
    except Exception as exc:
        logger.error("Unexpected error placing order: %s", exc)
        print(f"\n Order FAILED: {exc}")
        raise

    result_str = _build_order_result(response)
    print(result_str)
    logger.info("Order response:\n%s", result_str)

    status = response.get("status", "UNKNOWN")
    if status in {"FILLED", "NEW", "PARTIALLY_FILLED"}:
        print(f"\n Order placed successfully! Status: {status}")
        logger.info("Order SUCCESS — orderId=%s status=%s", response.get("orderId"), status)
    else:
        print(f"\n Order status: {status}")
        logger.warning("Unexpected order status: %s | response=%s", status, response)

    return response
