from line.models import MessageAction
from linebot.v3.messaging import (
    RichMenuArea,
    RichMenuBounds,
    RichMenuRequest,
    RichMenuSize,
)

RICH_MENU = RichMenuRequest(
    size=RichMenuSize(width=1200, height=810),
    selected=True,
    name="rich_menu",
    chatBarText="點擊開啟/關閉選單",
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=600, height=405),
            action=MessageAction(text="cmd=order", label="點餐"),
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=600, y=0, width=600, height=405),
            action=MessageAction(text="cmd=shop_info", label="店家資訊"),
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=405, width=600, height=405),
            action=MessageAction(text="cmd=reservation", label="訂位"),
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=600, y=405, width=600, height=405),
            action=MessageAction(text="cmd=account", label="會員"),
        ),
    ],
)
