from typing import Any, List, Optional

from line import Bot, Cog, Context, command
from line.models import (
    CarouselColumn,
    CarouselTemplate,
    ConfirmTemplate,
    PostbackAction,
    QuickReply,
    QuickReplyItem,
    TemplateMessage,
    TextMessage,
)

from ..models import Item, ItemCategory, User
from ..utils import get_now, split_list


class Cart:
    def __init__(self):
        self.items: List[Item] = []
        self.total_price = 0
        self.display_text = ""
        self.quick_reply: QuickReply

    async def create(self, item_ids: List[int]) -> "Cart":
        if not item_ids:
            self.display_text = "你目前尚未點選任何餐點"
            self.quick_reply = QuickReply(
                [QuickReplyItem(PostbackAction("cmd=order", "點餐"))]
            )
            return self
        for cart_item_id in set(item_ids):
            cart_item = await Item.get(id=cart_item_id)
            self.items.append(cart_item)
            item_amount = item_ids.count(cart_item_id)
            item_total_price = cart_item.price * item_amount
            self.total_price += item_total_price
            self.display_text += (
                f"{cart_item.name} x{item_amount} (NT$ {item_total_price})\n"
            )
        self.display_text += f"\n總金額: NT$ {self.total_price}"
        self.quick_reply = QuickReply(
            items=[
                QuickReplyItem(
                    PostbackAction("cmd=checkout", "結帳", display_text="請前往櫃台並向店員出示手機畫面")
                ),
                QuickReplyItem(
                    PostbackAction("cmd=order&is_continue_order=true", "繼續點餐")
                ),
                QuickReplyItem(PostbackAction("cmd=remove_item", "刪除餐點")),
            ]
        )
        return self


class OrderCog(Cog):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    @command
    async def order(
        self,
        ctx: Context,
        is_continue_order: bool = False,
        item_category: Optional[str] = None,
    ) -> Any:
        user = await User.get_or_none(id=ctx.user_id)
        if user is None:
            profile = await self.bot.line_bot_api.get_profile(ctx.user_id)
            user = await User.create(
                id=ctx.user_id,
                name=profile.display_name,
            )
        if user.cart and not is_continue_order:
            template = ConfirmTemplate(
                "系統偵測到你有尚未結帳的餐點, 是否要繼續點餐?",
                actions=[
                    PostbackAction("cmd=continue_order", "繼續點餐"),
                    PostbackAction("cmd=checkout", "結帳"),
                ],
            )
            return await ctx.reply_template("點餐", template)

        if not item_category:
            quick_reply_items = [
                QuickReplyItem(
                    PostbackAction(
                        f"cmd=order&is_continue_order=true&item_category={category.value}",
                        category.value,
                    )
                )
                for category in ItemCategory
            ]
            return await ctx.reply_text(
                "請選擇餐點類別", quick_reply=QuickReply(quick_reply_items)
            )

        all_items = await Item.all().filter(category=ItemCategory(item_category))
        if not all_items:
            return await ctx.reply_text(f"目前類別 {item_category} 沒有任何商品")

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
    async def continue_order(self, ctx: Context) -> Any:
        user = await User.get(id=ctx.user_id)
        cart = await Cart().create(user.cart)
        await ctx.reply_text(cart.display_text, quick_reply=cart.quick_reply)

    @command
    async def order_item(self, ctx: Context, item_id: int, amount: int) -> Any:
        user = await User.get(id=ctx.user_id)
        for _ in range(amount):
            user.cart.append(item_id)
        await user.save()

        cart = await Cart().create(user.cart)
        await ctx.reply_text(cart.display_text, quick_reply=cart.quick_reply)

    @command
    async def checkout(self, ctx: Context) -> Any:
        user = await User.get(id=ctx.user_id)
        cart = await Cart().create(user.cart)
        now_time_str = get_now().strftime("%Y-%m-%d %H:%M:%S")
        await ctx.reply_text(f"{user.name}\n{now_time_str}\n\n{cart.display_text}")
        user.cart.clear()
        await user.save()

    @command
    async def remove_item(
        self,
        ctx: Context,
        index: int = 0,
        item_id: Optional[int] = None,
        amount: Optional[int] = None,
    ) -> Any:
        user = await User.get(id=ctx.user_id)
        if item_id is None:
            cart = await Cart().create(user.cart)
            split_cart_items = split_list(cart.items, 11)
            quick_reply_items: List[QuickReplyItem] = []
            for item in split_cart_items[index]:
                quick_reply_items.append(
                    QuickReplyItem(
                        PostbackAction(
                            data="cmd=ignore",
                            label=item.name,
                            fill_in_text=f"cmd=remove_item&item_id={item.id}&amount=",
                            input_option="openKeyboard",
                            display_text="請輸入要刪除的餐點數量, 不輸入則刪除全部\n(請勿更動前面的英文指令)",
                        )
                    )
                )

            if index > 0:
                quick_reply_items.insert(
                    0,
                    QuickReplyItem(
                        action=PostbackAction(
                            label="上一頁", data=f"cmd=remove_item&index={index-1}"
                        )
                    ),
                )
            if index < len(split_cart_items) - 1:
                quick_reply_items.append(
                    QuickReplyItem(
                        action=PostbackAction(
                            label="下一頁", data=f"cmd=remove_item&index={index+1}"
                        )
                    )
                )
            await ctx.reply_text(
                "請選擇要刪除的餐點",
                quick_reply=QuickReply(quick_reply_items),
            )
        else:
            cart = await Cart().create(user.cart)
            current_amount = user.cart.count(item_id)
            delete_amount = amount or current_amount

            if delete_amount > current_amount:
                return await ctx.reply_multiple(
                    [
                        TextMessage(
                            f"錯誤:\n你輸入的刪除數量 [{delete_amount}] 大於你目前已點的餐點數量 [{current_amount}]"
                        ),
                        TextMessage(cart.display_text, quick_reply=cart.quick_reply),
                    ]
                )
            if delete_amount < 1:
                return await ctx.reply_multiple(
                    [
                        TextMessage("錯誤:\n你輸入的刪除數量小於 1"),
                        TextMessage(cart.display_text, quick_reply=cart.quick_reply),
                    ]
                )

            for _ in range(delete_amount):
                user.cart.remove(item_id)
            await user.save()

            cart = await Cart().create(user.cart)
            await ctx.reply_text(cart.display_text, quick_reply=cart.quick_reply)
