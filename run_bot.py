import asyncio
import os

from dotenv import load_dotenv

from restaurant_bot.bot import RestaurantBot


async def main() -> None:
    load_dotenv()
    channel_secret = os.getenv("LINE_CHANNEL_SECRET")
    access_token = os.getenv("LINE_ACCESS_TOKEN")
    if not (channel_secret and access_token):
        raise RuntimeError("LINE_CHANNEL_SECRET and LINE_ACCESS_TOKEN are required.")

    bot = RestaurantBot(
        channel_secret, access_token, os.getenv("DB_URL") or "sqlite://db.sqlite3"
    )
    await bot.run(port=7030, custom_route="/restaurant/line")


asyncio.run(main())
