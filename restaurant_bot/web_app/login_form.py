import flet as ft

from ..models import User


class LoginForm(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.name = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()

    async def login(self, e: ft.ControlEvent):
        name = self.name.current.value
        password = self.password.current.value
        user = await User.get_or_none(name=name, password=password)
        if user is None:
            self.name.current.error_text = "帳號或密碼錯誤"
            self.password.current.error_text = "帳號或密碼錯誤"
            await self.name.current.update_async()
            await self.password.current.update_async()
            return
        e.page.session.set("authed", True)
        e.page.views.pop()
        await e.page.update_async()
        await e.page.go_async("/items/refresh")

    def build(self):
        return ft.Container(
            ft.Column(
                [
                    ft.Container(
                        ft.Text("餐廳後台", size=24, weight=ft.FontWeight.W_700),
                        margin=ft.margin.only(bottom=16),
                    ),
                    ft.TextField(ref=self.name, label="帳戶名稱", icon=ft.icons.PERSON),
                    ft.TextField(
                        ref=self.password,
                        label="密碼",
                        password=True,
                        can_reveal_password=True,
                        icon=ft.icons.KEY,
                    ),
                    ft.Container(
                        ft.Row(
                            [ft.FilledButton("登入", on_click=self.login)],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        margin=ft.margin.only(top=8),
                    ),
                ]
            ),
        )
