

import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from binance.exceptions import BinanceAPIException, BinanceRequestException

load_dotenv()

from client import BinanceClientWrapper
from logging_config import setup_logger
from orders import place_order
from validators import ValidationError

logger = setup_logger("trading_bot.cli")


def _get_client() -> BinanceClientWrapper:
    api_key = os.getenv("BINANCE_TESTNET_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "").strip()

    if not api_key or not api_secret:
        click.echo(
            "API credentials not found.\n"
            "   Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET\n"
            "   in your environment or in a .env file.",
            err=True,
        )
        sys.exit(1)

    return BinanceClientWrapper(api_key=api_key, api_secret=api_secret)



@click.group()
@click.version_option("1.0.0", prog_name="trading-bot")
def cli():
    """Binance Futures Testnet Trading Bot — place MARKET, LIMIT, and STOP orders."""




@cli.command("place-order")
@click.option("--symbol", "-s", required=True, help="Trading symbol, e.g. BTCUSDT")
@click.option(
    "--side", "-d",
    required=True,
    type=click.Choice(["BUY", "SELL"], case_sensitive=False),
    help="Order side: BUY or SELL",
)
@click.option(
    "--type", "-t", "order_type",
    required=True,
    type=click.Choice(["MARKET", "LIMIT", "STOP", "STOP_MARKET"], case_sensitive=False),
    help="Order type",
)
@click.option("--quantity", "-q", required=True, type=float, help="Order quantity")
@click.option(
    "--price", "-p",
    default=None, type=float,
    help="Limit price (required for LIMIT / STOP orders)",
)
@click.option(
    "--stop-price",
    default=None, type=float,
    help="Stop trigger price (required for STOP / STOP_MARKET orders)",
)
def place_order_cmd(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
):
    
    client = _get_client()

    try:
        place_order(
            client=client,
            symbol=symbol,
            side=side.upper(),
            order_type=order_type.upper(),
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        click.echo(f"Validation error: {exc}", err=True)
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except BinanceAPIException as exc:
        click.echo(f"Binance API error [{exc.code}]: {exc.message}", err=True)
        sys.exit(1)
    except BinanceRequestException as exc:
        click.echo(f" Network/request error: {exc.message}", err=True)
        sys.exit(1)




@cli.command("account")
def account_cmd():
    """Show Binance Futures Testnet account balances."""
    client = _get_client()

    try:
        data = client.get_account()
    except BinanceAPIException as exc:
        click.echo(f" Binance API error [{exc.code}]: {exc.message}", err=True)
        sys.exit(1)

    assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) > 0]
    if not assets:
        click.echo("No assets with non-zero balance found.")
        return

    click.echo("\n┌─ Account Balances ───────────────────────────")
    for asset in assets:
        click.echo(
            f"│  {asset['asset']:8s}  wallet={float(asset['walletBalance']):.4f}"
            f"  unrealized PnL={float(asset.get('unrealizedProfit', 0)):.4f}"
        )
    click.echo("└──────────────────────────────────────────────\n")


@cli.command("server-time")
def server_time_cmd():
    """Fetch Binance server time — use as a connectivity check."""
    client = _get_client()
    try:
        ts = client.get_server_time()
        click.echo(f"Binance Testnet server time: {ts} ms")
    except BinanceAPIException as exc:
        click.echo(f" [{exc.code}]: {exc.message}", err=True)
        sys.exit(1)



if __name__ == "__main__":
    cli()
