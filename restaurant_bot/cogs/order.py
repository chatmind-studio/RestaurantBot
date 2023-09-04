from typing import Any, List

from line import Bot, Cog, Context, command
from line.models import (
    CarouselColumn,
    CarouselTemplate,
    ConfirmTemplate,
    PostbackAction,
    TemplateMessage,
)

from ..models import Item
from ..utils import split_list


class OrderCog(Cog):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    @command
    async def order(self, ctx: Context) -> Any:
        all_items = await Item.all()
        if not all_items:
            return await ctx.reply_text("目前沒有任何商品")

        all_items.reverse()
        split_items = split_list(all_items, 10)
        templates: List[CarouselTemplate] = []
        for items in split_items:
            columns: List[CarouselColumn] = []
            for item in items:
                column = CarouselColumn(
                    thumbnail_image_url=item.image_url
                    or "https://i.ibb.co/h7sVKj2/Frame-5.png",
                    title=item.name,
                    text=f"{item.price} 元\n{item.description[:20]}",
                    actions=[
                        PostbackAction(
                            label="點一份",
                            data=f"cmd=confirm_order&item_id={item.id}&item_name={item.name}&item_price={item.price}&amount=1",
                        ),
                        PostbackAction(
                            label="點兩份",
                            data=f"cmd=confirm_order&item_id={item.id}&item_name={item.name}&item_price={item.price}&amount=2",
                        ),
                        PostbackAction(
                            label="點三份",
                            data=f"cmd=confirm_order&item_id={item.id}&item_name={item.name}&item_price={item.price}&amount=3",
                        ),
                    ],
                )
                columns.append(column)
            templates.append(CarouselTemplate(columns=columns))

        await ctx.reply_multiple(
            [TemplateMessage("點餐", template) for template in templates]
        )

    @command
    async def confirm_order(
        self, ctx: Context, item_id: int, item_name: str, item_price: int, amount: int
    ) -> Any:
        await ctx.reply_template(
            "確認點餐",
            ConfirmTemplate(
                f"確定要點 {amount} 份的 {item_name} 嗎?\n這樣一共是 {item_price * amount} 元",
                actions=[
                    PostbackAction(label="取消", data="cmd=order", display_text="已取消"),
                    PostbackAction(
                        label="確定",
                        data=f"cmd=order_item&item_id={item_id}&amount={amount}",
                    ),
                ],
            ),
        )

    @command
    async def order_item(self, ctx: Context, item_id: int, amount: int) -> Any:
        item = await Item.get_or_none(id=item_id)
        if not item:
            return await ctx.reply_text("找不到這個商品")
        await ctx.reply_text(f"已經幫你點 {amount} 份的 {item.name} 了")
