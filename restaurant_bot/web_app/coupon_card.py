import flet as ft

from ..models import Coupon
from .coupon_form import CouponForm


class CouponCard(ft.UserControl):
    def __init__(self, coupon: Coupon):
        super().__init__()
        self.coupon = coupon
        self.dialog = ft.Ref[ft.AlertDialog]()

    async def edit_item(self, e: ft.ControlEvent):
        page: ft.Page = e.page
        page.views.append(
            ft.View(controls=[CouponForm(is_create=False, coupon=self.coupon)])
        )
        await page.update_async()
        await page.go_async("/coupon/refresh")

    async def delete_item(self, e: ft.ControlEvent):
        page: ft.Page = e.page
        dialog = ft.AlertDialog(
            ref=self.dialog,
            modal=True,
            title=ft.Text("刪除餐點"),
            content=ft.Text("確定要刪除這個餐點嗎?\n(刪除後無法復原)"),
            actions=[
                ft.TextButton("取消", on_click=self.dialog_cancel),
                ft.TextButton("刪除", on_click=self.dialog_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        await page.update_async()

    async def dialog_cancel(self, e: ft.ControlEvent):
        self.dialog.current.open = False
        await e.page.update_async()

    async def dialog_delete(self, e: ft.ControlEvent):
        await Coupon.filter(id=self.coupon.id).delete()
        self.dialog.current.open = False
        await e.page.update_async()
        await e.page.go_async("/coupons/refresh")

    def build(self):
        return ft.Card(
            ft.Column(
                [
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text(
                                    self.coupon.name,
                                    size=22,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.Text(
                                    f"於 {self.coupon.expire_date.strftime('%Y/%m/%d')} 到期",
                                    size=18,
                                ),
                                ft.Text(self.coupon.description),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.OutlinedButton(
                                                "刪除", on_click=self.delete_item
                                            ),
                                            ft.FilledButton(
                                                "編輯", on_click=self.edit_item
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                    ),
                                    margin=ft.margin.only(top=8),
                                ),
                            ],
                        ),
                        padding=12,
                    ),
                ]
            )
        )
