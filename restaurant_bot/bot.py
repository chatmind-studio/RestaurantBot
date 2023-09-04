import logging
from pathlib import Path

from line import Bot
from tortoise import Tortoise

from .rich_menu import RICH_MENU


class RestaurantBot(Bot):
    def __init__(self, channel_secret: str, access_token: str, db_url: str) -> None:
        super().__init__(channel_secret=channel_secret, access_token=access_token)
        self.db_url = db_url

    async def _setup_rich_menu(self) -> None:
        result = await self.line_bot_api.create_rich_menu(RICH_MENU)
        with open("data/rich_menu.png", "rb") as f:
            await self.blob_api.set_rich_menu_image(
                result.rich_menu_id,
                body=bytearray(f.read()),
                _headers={"Content-Type": "image/png"},
            )
        await self.line_bot_api.set_default_rich_menu(result.rich_menu_id)

    async def setup_hook(self) -> None:
        for cog in Path("restaurant_bot/cogs").glob("*.py"):
            if cog.stem == "__init__":
                continue
            logging.info("Loading cog %s", cog.stem)
            self.add_cog(f"restaurant_bot.cogs.{cog.stem}")

        logging.info("Setting up rich menu")
        await self._setup_rich_menu()
        logging.info("Setting up database")
        await Tortoise.init(
            db_url="sqlite://db.sqlite3",
            modules={"models": ["restaurant_bot.models"]},
        )
        await Tortoise.generate_schemas()

    async def on_close(self) -> None:
        await Tortoise.close_connections()
