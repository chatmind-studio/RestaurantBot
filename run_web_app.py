import asyncio

import flet as ft
from tortoise import Tortoise

from restaurant_bot.models import Item
from restaurant_bot.web_app.item_card import ItemCard
from restaurant_bot.web_app.item_form import ItemForm

ROUTES = {
    0: "/items",
    1: "/coupons",
}


async def main(page: ft.Page):
    async def on_click(_: ft.ControlEvent):
        page.views.append(ft.View(controls=[ItemForm()]))
        await page.update_async()

    async def on_route_change(e: ft.RouteChangeEvent):
        page.controls = []
        page.controls.append(
            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=on_click)
        )
        if e.route == "/items/refresh":
            return await page.go_async("/items")

        if e.route == "/items":
            items = await Item.all()
            if not items:
                return page.controls.append(
                    ft.Container(
                        ft.Text("目前沒有任何餐點, 點擊右下角按鈕新增餐點"),
                        alignment=ft.alignment.center,
                    )
                )

            grid = ft.ListView(expand=True, spacing=12)
            for item in reversed(items):
                card = ItemCard(item)
                grid.controls.append(card)
            page.controls.append(grid)

        await page.update_async()

    async def on_change(e: ft.ControlEvent):
        await e.page.go_async(ROUTES[e.control.selected_index])

    page.on_route_change = on_route_change
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationDestination(
                icon=ft.icons.LUNCH_DINING_OUTLINED,
                selected_icon=ft.icons.LUNCH_DINING,
                label="餐點",
            ),
            ft.NavigationDestination(
                icon_content=ft.Icon(ft.icons.SELL_OUTLINED),
                selected_icon_content=ft.Icon(ft.icons.SELL),
                label="優惠卷",
            ),
        ],
        on_change=on_change,
    )
    await page.go_async("/items")


loop = asyncio.get_event_loop()
loop.run_until_complete(
    Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models": ["restaurant_bot.models"]},
    )
)
loop.run_until_complete(Tortoise.generate_schemas())
ft.app(target=main, port=5000, upload_dir="uploads")


loop = asyncio.get_event_loop()
loop.run_until_complete(Tortoise.close_connections())
loop.close()
