from typing import Optional

import flet as ft

from ..models import Item, ItemCategory


class ItemForm(ft.UserControl):
    def __init__(self, *, is_create: bool = True, item: Optional[Item] = None) -> None:
        super().__init__()
        self.name = ft.Ref[ft.TextField]()
        self.description = ft.Ref[ft.TextField]()
        self.category = ft.Ref[ft.Dropdown]()
        self.price = ft.Ref[ft.TextField]()
        self.image_url = ft.Ref[ft.TextField]()

        self.is_create = is_create
        self.item = item

    async def create_or_update_item(
        self,
        name: str,
        description: str,
        category: ItemCategory,
        price: int,
        image_url: Optional[str],
    ) -> None:
        if self.is_create:
            await Item.create(
                name=name,
                description=description,
                category=category,
                price=price,
                image_url=image_url,
            )
        else:
            assert self.item
            await Item.filter(id=self.item.id).update(
                name=name,
                description=description,
                category=category,
                price=price,
                image_url=image_url,
            )

    async def submit(self, e: ft.ControlEvent) -> None:
        if not self.name.current.value:
            self.name.current.error_text = "這個欄位是必填的"
            await self.name.current.update_async()
        if not self.description.current.value:
            self.description.current.error_text = "這個欄位是必填的"
            await self.description.current.update_async()
        if not self.price.current.value:
            self.price.current.error_text = "這個欄位是必填的"
            if self.price.current.value and not self.price.current.value.isdigit():
                self.price.current.error_text = "這個欄位必須是數字"
            await self.price.current.update_async()

        if not (
            self.name.current.value
            and self.description.current.value
            and self.price.current.value
            and self.category.current.value
        ):
            return
        if not self.price.current.value.isdigit():
            return

        await self.create_or_update_item(
            name=self.name.current.value,
            description=self.description.current.value,
            category=ItemCategory(self.category.current.value),
            price=int(self.price.current.value),
            image_url=self.image_url.current.value,
        )
        e.page.views.pop()
        await e.page.update_async()
        await e.page.go_async("/items/refresh")

    @staticmethod
    async def cancel(e: ft.ControlEvent) -> None:
        e.page.views.pop()
        await e.page.update_async()

    @staticmethod
    async def validate_number_field(e: ft.ControlEvent):
        control: ft.TextField = e.control
        if not control.value:
            control.error_text = "這個欄位是必填的"
        elif not control.value.isdigit():
            control.error_text = "這個欄位必須是數字"
        else:
            control.error_text = None
        await control.update_async()

    @staticmethod
    async def validate_required_field(e: ft.ControlEvent):
        control: ft.TextField = e.control
        if not control.value:
            control.error_text = "這個欄位是必填的"
        else:
            control.error_text = None
        await control.update_async()

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
                                    "新增餐點" if self.is_create else "編輯餐點",
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
                                        hint_text="起司火腿堡, 起司蛋餅...",
                                        autofocus=True,
                                        icon=ft.icons.TITLE,
                                        on_blur=self.validate_required_field,
                                        value=self.item.name if self.item else None,
                                    ),
                                    ft.TextField(
                                        ref=self.description,
                                        label="敘述",
                                        multiline=True,
                                        max_length=50,
                                        keyboard_type=ft.KeyboardType.MULTILINE,
                                        hint_text="柔軟的麵包, 搭配融化的起司...\n(可換行)",
                                        icon=ft.icons.DESCRIPTION,
                                        on_blur=self.validate_required_field,
                                        value=self.item.description
                                        if self.item
                                        else None,
                                    ),
                                    ft.Dropdown(
                                        ref=self.category,
                                        icon=ft.icons.CATEGORY,
                                        label="類別",
                                        options=[
                                            ft.dropdown.Option(c.value)
                                            for c in ItemCategory
                                        ],
                                        value=self.item.category.value
                                        if self.item
                                        else ItemCategory.FOOD.value,
                                    ),
                                    ft.TextField(
                                        ref=self.price,
                                        icon=ft.icons.ATTACH_MONEY,
                                        label="價格",
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                        prefix_text="NT$",
                                        on_blur=self.validate_number_field,
                                        value=str(self.item.price)
                                        if self.item
                                        else None,
                                    ),
                                    ft.TextField(
                                        ref=self.image_url,
                                        icon=ft.icons.IMAGE,
                                        label="圖片網址",
                                        hint_text="https://i.ibb.co/h7sVKj2/image.png",
                                        value=self.item.image_url
                                        if self.item
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
