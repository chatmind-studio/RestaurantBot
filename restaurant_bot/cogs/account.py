from typing import Any, List, Optional

import qrcode
from line import Bot, Cog, Context, command
from line.models import (
    ButtonsTemplate,
    PostbackAction,
    QuickReply,
    QuickReplyItem,
    URIAction,
)

from ..models import Coupon, User
from ..utils import split_list, upload_image


class AccountCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(bot)

    @command
    async def account(self, ctx: Context) -> Any:
        user = await User.get_or_none(id=ctx.user_id)
        if user is None:
            profile = await self.bot.line_bot_api.get_profile(ctx.user_id)
            user = await User.create(
                id=ctx.user_id,
                name=profile.display_name,
            )

        actions: List[PostbackAction | URIAction] = [
            PostbackAction(
                label="集點",
                data="cmd=earn_points",
                display_text="請讓店員掃描下方的 QR Code, 完成後點擊「會員」可確認點數是否成功入賬",
            ),
            PostbackAction(
                label="獲得優惠卷",
                data="cmd=earn_coupon",
                display_text="請讓店員掃描下方的 QR Code, 完成後點擊「會員」可確認優惠卷是否成功入賬",
            ),
        ]
        if user.coupon_ids:
            actions.append(
                PostbackAction(
                    label="我的優惠券",
                    data="cmd=show_coupons",
                ),
            )
        if user.is_admin:
            actions.append(
                URIAction(
                    label="餐廳後台",
                    uri="https://restaurant-web-app.seriaati.xyz/?openExternalBrowser=1",
                ),
            )
        template = ButtonsTemplate(
            title=f"你好, {user.name}",
            text=f"點數: {user.points} 點\n優惠券: {len(user.coupon_ids)} 張\n身份: {'管理員' if user.is_admin else '會員'}",
            actions=actions,  # type: ignore
        )
        await ctx.reply_template(alt_text="會員", template=template)

    @command
    async def show_coupons(self, ctx: Context, index: int = 0) -> Any:
        user = await User.get(id=ctx.user_id)
        all_coupon_ids = user.coupon_ids
        split_coupon_ids = split_list(list(set(all_coupon_ids)), 11)

        items: List[QuickReplyItem] = []
        for coupon_id in split_coupon_ids[index]:
            coupon = await Coupon.get(id=coupon_id)
            coupon_count = all_coupon_ids.count(coupon_id)
            item = QuickReplyItem(
                action=PostbackAction(
                    label=f"{coupon.name} x{coupon_count}",
                    data=f"cmd=coupon_detail&coupon_id={coupon.id}",
                )
            )
            items.append(item)
        if index > 0:
            items.insert(
                0,
                QuickReplyItem(
                    action=PostbackAction(
                        label="上一頁", data=f"cmd=show_coupons&index={index-1}"
                    )
                ),
            )
        if index < len(split_coupon_ids) - 1:
            items.append(
                QuickReplyItem(
                    action=PostbackAction(
                        label="下一頁", data=f"cmd=show_coupons&index={index+1}"
                    )
                )
            )

        await ctx.reply_text(
            "請從下方選擇要使用的優惠卷",
            quick_reply=QuickReply(items=items),
        )

    @command
    async def coupon_detail(self, ctx: Context, coupon_id: int) -> Any:
        coupon = await Coupon.get(id=coupon_id)
        template = ButtonsTemplate(
            title=coupon.name,
            text=coupon.description,
            actions=[
                PostbackAction(
                    label="使用",
                    data=f"cmd=use_coupon&coupon_id={coupon.id}",
                ),
            ],
        )
        await ctx.reply_template(alt_text="優惠卷", template=template)

    @command
    async def use_coupon(self, ctx: Context, coupon_id: int) -> Any:
        coupon = await Coupon.get(id=coupon_id)
        user = await User.get(id=ctx.user_id)
        user.coupon_ids.remove(coupon.id)
        await user.save()
        await ctx.reply_text(text=f"成功使用 {coupon.name} 優惠卷")

    @command
    async def earn_coupon(
        self, ctx: Context, index: int = 0, user_id: Optional[str] = None
    ) -> Any:
        if not user_id:
            url = f"https://line.me/R/oaMessage/%40402kzhrk/?cmd=earn_coupon&user_id={ctx.user_id}"
            image = qrcode.make(url)
            image_url = await upload_image(image)
            return await ctx.reply_image(image_url)

        command_user = await User.get(id=ctx.user_id)
        if not command_user.is_admin:
            return await ctx.reply_text(text="你不是管理員")

        all_coupons = await Coupon.all()
        if not all_coupons:
            return await ctx.reply_text(text="目前沒有優惠卷, 請從後台中新增")
        split_coupons = split_list(all_coupons, 11)

        items: List[QuickReplyItem] = []
        for coupon in split_coupons[index]:
            item = QuickReplyItem(
                action=PostbackAction(
                    label=coupon.name,
                    data=f"cmd=give_coupon&coupon_id={coupon.id}&user_id={user_id}",
                )
            )
            items.append(item)
        if index > 0:
            items.insert(
                0,
                QuickReplyItem(
                    action=PostbackAction(
                        label="上一頁",
                        data=f"cmd=earn_coupon&index={index-1}&user_id={user_id}",
                    )
                ),
            )
        if index < len(split_coupons) - 1:
            items.append(
                QuickReplyItem(
                    action=PostbackAction(
                        label="下一頁",
                        data=f"cmd=earn_coupon&index={index+1}&user_id={user_id}",
                    )
                )
            )

        await ctx.reply_text(
            "請從下方選擇要給予的優惠卷",
            quick_reply=QuickReply(items=items),
        )

    @command
    async def give_coupon(self, ctx: Context, user_id: str, coupon_id: int) -> Any:
        user_to_give_coupon = await User.get(id=user_id)
        command_user = await User.get(id=ctx.user_id)
        if not command_user.is_admin:
            return await ctx.reply_text(text="你不是管理員")

        coupon = await Coupon.get(id=coupon_id)
        user_to_give_coupon.coupon_ids.append(coupon.id)
        await user_to_give_coupon.save()
        await ctx.reply_text(
            text=f"成功, 已給予 {user_to_give_coupon.name} {coupon.name} 優惠卷"
        )

    @command
    async def earn_points(self, ctx: Context, user_id: Optional[str] = None) -> Any:
        if not user_id:
            url = f"https://line.me/R/oaMessage/%40402kzhrk/?cmd=earn_points&user_id={ctx.user_id}"
            image = qrcode.make(url)
            image_url = await upload_image(image)
            return await ctx.reply_image(image_url)

        user_to_give_point = await User.get(id=user_id)
        command_user = await User.get(id=ctx.user_id)
        if not command_user.is_admin:
            return await ctx.reply_text(text="你不是管理員")

        template = ButtonsTemplate(
            title=f"你好, {command_user.name}",
            text=f"點擊下方的按鈕後, 輸入要給予 {user_to_give_point.name} 的點數數量",
            actions=[
                PostbackAction(
                    label="輸入點數",
                    data="ignore",
                    display_text="請輸入點數",
                    input_option="openKeyboard",
                    fill_in_text=f"cmd=give_points&user_id={user_id}&points=",
                ),
            ],
        )
        await ctx.reply_template(
            alt_text=f"要給予 {user_to_give_point.name} 多少點?", template=template
        )

    @command
    async def give_points(self, ctx: Context, user_id: str, points: int) -> Any:
        user_to_give_point = await User.get(id=user_id)
        command_user = await User.get(id=ctx.user_id)
        if not command_user.is_admin:
            return await ctx.reply_text(text="你不是管理員")

        user_to_give_point.points += points
        await user_to_give_point.save()
        await ctx.reply_text(text=f"成功, 已給予 {user_to_give_point.name} {points} 點")
