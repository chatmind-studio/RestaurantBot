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

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is required.")
    bot = RestaurantBot(channel_secret, access_token, db_url)
    await bot.run()


asyncio.run(main())
