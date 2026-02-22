

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from logging_config import setup_logger

TESTNET_FUTURES_URL = "https://testnet.binancefuture.com"

logger = setup_logger("trading_bot.client")


class BinanceClientWrapper:

    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True,          )
        self.client.FUTURES_URL = TESTNET_FUTURES_URL + "/fapi"
        logger.info("BinanceClient initialised (Futures Testnet)")

    def get_server_time(self) -> int:
        data = self.client.futures_time()
        ts = data["serverTime"]
        logger.debug("Server time: %s", ts)
        return ts

    def get_exchange_info(self) -> dict:
        return self.client.futures_exchange_info()

    def get_account(self) -> dict:
        logger.debug("Fetching account info")
        return self.client.futures_account()

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "GTC",
    ) -> dict:
        
        kwargs: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            kwargs["price"] = price
            kwargs["timeInForce"] = time_in_force

        if order_type == "STOP":
            kwargs["price"] = price
            kwargs["stopPrice"] = stop_price
            kwargs["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            kwargs["stopPrice"] = stop_price

        logger.debug("Calling futures_create_order with: %s", kwargs)
        try:
            response = self.client.futures_create_order(**kwargs)
        except BinanceAPIException as exc:
            logger.error(
                "BinanceAPIException: status=%s code=%s msg=%s",
                exc.status_code, exc.code, exc.message,
            )
            raise
        except BinanceRequestException as exc:
            logger.error("BinanceRequestException: %s", exc.message)
            raise

        logger.debug("futures_create_order response: %s", response)
        return response
