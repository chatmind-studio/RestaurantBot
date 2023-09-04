from typing import Any, List, Optional

import qrcode
from line import Bot, Cog, Context, command
from line.models import ButtonsTemplate, PostbackAction, QuickReply, QuickReplyItem

from ..models import Coupon, User
from ..utils import split_list, upload_image


class AccountCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(bot)

    @command
    async def account(self, ctx: Context) -> Any:
        profile = await ctx.api.get_profile(ctx.user_id)
        user, _ = await User.get_or_create(id=ctx.user_id, name=profile.display_name)
        await user.fetch_related("coupons")
        actions = [
            PostbackAction(
                label="集點",
                data="cmd=earn_points",
                display_text="請讓店員掃描下方的 QR Code, 完成後點擊「會員」可確認點數是否成功入賬",
            ),
        ]
        if user.coupons:
            actions.append(
                PostbackAction(
                    label="我的優惠券",
                    data="cmd=show_coupons",
                ),
            )
        if user.is_admin:
            actions.append(
                PostbackAction(
                    label="管理員界面",
                    data="cmd=admin_menu",
                ),
            )
        template = ButtonsTemplate(
            title=f"你好, {user.name}",
            text=f"點數: {user.points} 點\n優惠券: {len(user.coupons)} 張\n身份: {'管理員' if user.is_admin else '會員'}",
            actions=actions,  # type: ignore
        )
        await ctx.reply_template(alt_text="會員", template=template)

    @command
    async def show_coupons(self, ctx: Context, index: int = 0) -> Any:
        user = await User.filter(id=ctx.user_id).first()
        if not user:
            return
        all_coupons = list(set(user.coupons))
        split_coupons = split_list(all_coupons, 11)
        items: List[QuickReplyItem] = []
        for coupon in split_coupons[index]:
            item = QuickReplyItem(
                action=PostbackAction(
                    label=coupon.name,
                    data=f"cmd=show_coupon&coupon_id={coupon.id}",
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
        if index < len(split_coupons) - 1:
            items.append(
                QuickReplyItem(
                    action=PostbackAction(
                        label="下一頁", data=f"cmd=show_coupons&index={index+1}"
                    )
                )
            )
        await ctx.reply_text(
            text="請從下方選擇要使用的優惠卷",
            quick_reply=QuickReply(items=items),
        )

    @command
    async def show_coupon(self, ctx: Context, coupon_id: str) -> Any:
        coupon = await Coupon.filter(id=coupon_id).first()
        if coupon:
            await ctx.reply_text(text=coupon.description)
        else:
            await ctx.reply_text(text="找不到該優惠卷")

    @command
    async def earn_points(self, ctx: Context, user_id: Optional[str] = None) -> Any:
        if not user_id:
            url = f"https://line.me/R/oaMessage/%40402kzhrk/?cmd=earn_points&user_id={ctx.user_id}"
            image = qrcode.make(url)
            image_url = await upload_image(image)
            return await ctx.reply_image(image_url)

        user = await User.filter(id=user_id).first()
        if not user:
            return
        admin = await User.filter(id=ctx.user_id).first()
        if not admin or not admin.is_admin:
            return
        template = ButtonsTemplate(
            title=f"你好, {admin.name}",
            text=f"點擊下方的按鈕後, 輸入要給予 {user.name} 的點數數量",
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
        await ctx.reply_template(alt_text=f"要給予 {user.name} 多少點?", template=template)

    @command
    async def give_points(self, ctx: Context, user_id: str, points: int) -> Any:
        user = await User.filter(id=user_id).first()
        if not user:
            return
        admin = await User.filter(id=ctx.user_id).first()
        if not admin or not admin.is_admin:
            return
        user.points += points
        await user.save()
        await ctx.reply_text(text=f"成功, 已給予 {user.name} {points} 點")
