import flet as ft

from ..models import Item
from .item_form import ItemForm


class ItemCard(ft.UserControl):
    def __init__(self, item: Item):
        super().__init__()
        self.item = item
        self.dialog = ft.Ref[ft.AlertDialog]()

    async def edit_item(self, e: ft.ControlEvent):
        page: ft.Page = e.page
        page.views.append(ft.View(controls=[ItemForm(is_create=False, item=self.item)]))
        await page.update_async()
        await page.go_async("/items/refresh")

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
        await Item.filter(id=self.item.id).delete()
        self.dialog.current.open = False
        await e.page.update_async()
        await e.page.go_async("/items/refresh")

    def build(self):
        return ft.Card(
            ft.Column(
                [
                    ft.Image(
                        src=self.item.image_url
                        or "https://i.ibb.co/h7sVKj2/Frame-5.png",
                        border_radius=ft.border_radius.all(12),
                        fit=ft.ImageFit.COVER,
                        height=170,
                        width=400,
                    ),
                    ft.Container(
                        ft.Column(
                            [
                                ft.Text(
                                    f"{self.item.category}/{self.item.name}",
                                    size=22,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.Text(f"NT$ {self.item.price}", size=18),
                                ft.Text(self.item.description),
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
