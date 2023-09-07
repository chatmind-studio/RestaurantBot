import asyncio
import os

import flet as ft
from dotenv import load_dotenv
from tortoise import Tortoise

from restaurant_bot.models import Coupon, Item
from restaurant_bot.web_app import CouponCard, CouponForm, ItemCard, ItemForm, LoginForm

load_dotenv()

ROUTES = {
    0: "/items",
    1: "/coupons",
}


async def main(page: ft.Page):
    async def on_click(e: ft.ControlEvent):
        if e.page.route == "/items":
            page.views.append(ft.View(controls=[ItemForm()]))
            await page.update_async()
        elif e.page.route == "/coupons":
            page.views.append(ft.View(controls=[CouponForm()]))
            await page.update_async()

    async def on_route_change(e: ft.RouteChangeEvent):
        page.controls = []

        if not e.page.session.get("authed"):
            page.views.append(ft.View(controls=[LoginForm()]))
            await page.update_async()
            return

        if e.route == "/items/refresh":
            await page.go_async("/items")
        elif e.route == "/items":
            items = await Item.all()
            if not items:
                return page.controls.append(
                    ft.Container(
                        ft.Text("目前沒有任何餐點, 點擊右下角按鈕新增餐點"),
                        alignment=ft.alignment.center,
                    )
                )

            list_view = ft.ListView(expand=True, spacing=12)
            for item in reversed(items):
                card = ItemCard(item)
                list_view.controls.append(card)
            page.controls.append(list_view)
            await page.update_async()
        elif e.route == "/coupons/refresh":
            await page.go_async("/coupons")
        elif e.route == "/coupons":
            coupons = await Coupon.all()
            if not coupons:
                return page.controls.append(
                    ft.Container(
                        ft.Text("目前沒有任何優惠卷, 點擊右下角按鈕新增優惠卷"),
                        alignment=ft.alignment.center,
                    )
                )

            list_view = ft.ListView(expand=True, spacing=12)
            for coupon in reversed(coupons):
                card = CouponCard(coupon)
                list_view.controls.append(card)
            page.controls.append(list_view)
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
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.icons.ADD, on_click=on_click
    )
    await page.go_async("/items")


loop = asyncio.get_event_loop()
loop.run_until_complete(
    Tortoise.init(
        db_url=os.getenv("DB_URL") or "sqlite://db.sqlite3",
        modules={"models": ["restaurant_bot.models"]},
    )
)
loop.run_until_complete(Tortoise.generate_schemas())
ft.app(target=main, port=7031, view=None)


loop = asyncio.get_event_loop()
loop.run_until_complete(Tortoise.close_connections())
loop.close()
