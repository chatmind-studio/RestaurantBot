import datetime
from typing import Optional

import flet as ft

from ..models import Coupon
from ..utils import get_now


class CouponForm(ft.UserControl):
    def __init__(self, *, is_create: bool = True, coupon: Optional[Coupon] = None):
        super().__init__()
        self.name = ft.Ref[ft.TextField]()
        self.description = ft.Ref[ft.TextField]()
        self.expire_date = ft.Ref[ft.TextField]()

        self.is_create = is_create
        self.coupon = coupon

    @staticmethod
    async def cancel(e: ft.ControlEvent) -> None:
        e.page.views.pop()
        await e.page.update_async()

    @staticmethod
    async def validate_required_field(e: ft.ControlEvent):
        control: ft.TextField = e.control
        if not control.value:
            control.error_text = "這個欄位是必填的"
        else:
            control.error_text = None
        await control.update_async()

    async def submit(self, e: ft.ControlEvent) -> None:
        name = self.name.current
        description = self.description.current
        expire_date = self.expire_date.current
        if name.error_text or description.error_text or expire_date.error_text:
            return
        if not (name.value and description.value and expire_date.value):
            return
        try:
            converted_expire_date = datetime.datetime.strptime(
                expire_date.value, "%Y/%m/%d"
            ).date()
        except ValueError:
            expire_date.error_text = "日期格式錯誤"
            await expire_date.update_async()
            return

        if converted_expire_date < get_now().date():
            expire_date.error_text = "到期日必須是未來的日期"
            await expire_date.update_async()
            return

        if self.is_create:
            await Coupon.create(
                name=name.value,
                description=description.value,
                expire_date=converted_expire_date,
            )
        else:
            assert self.coupon
            await Coupon.filter(id=self.coupon.id).update(
                name=name.value,
                description=description.value,
                expire_date=converted_expire_date,
            )

        e.page.views.pop()
        await e.page.update_async()
        await e.page.go_async("/coupons/refresh")

    def build(self):
        return ft.SafeArea(
            ft.Container(
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.IconButton(
                                    ft.icons.ARROW_BACK, on_click=self.cancel
                                ),
                                ft.Text(
                                    "新增優惠卷" if self.is_create else "編輯優惠卷",
                                    size=24,
                                    weight=ft.FontWeight.W_700,
                                ),
                            ]
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.TextField(
                                        ref=self.name,
                                        label="名稱",
                                        max_length=20,
                                        hint_text="買一送一, 第二件飲品五折...",
                                        autofocus=True,
                                        icon=ft.icons.TITLE,
                                        on_blur=self.validate_required_field,
                                        value=self.coupon.name if self.coupon else None,
                                    ),
                                    ft.TextField(
                                        ref=self.description,
                                        label="敘述",
                                        multiline=True,
                                        max_length=50,
                                        keyboard_type=ft.KeyboardType.MULTILINE,
                                        hint_text="需滿額 300 元才可使用...\n(可換行)",
                                        icon=ft.icons.DESCRIPTION,
                                        on_blur=self.validate_required_field,
                                        value=self.coupon.description
                                        if self.coupon
                                        else None,
                                    ),
                                    ft.TextField(
                                        ref=self.expire_date,
                                        label="到期日",
                                        hint_text="2023/12/31",
                                        icon=ft.icons.CALENDAR_TODAY,
                                        on_blur=self.validate_required_field,
                                        value=self.coupon.expire_date.strftime(
                                            "%Y/%m/%d"
                                        )
                                        if self.coupon
                                        else None,
                                    ),
                                ],
                                spacing=12,
                            ),
                            margin=ft.margin.only(top=12),
                        ),
                        ft.Container(
                            ft.FilledButton(
                                "送出" if self.is_create else "儲存", on_click=self.submit
                            ),
                            alignment=ft.alignment.center_right,
                            margin=ft.margin.only(top=8),
                        ),
                    ]
                )
            )
        )
