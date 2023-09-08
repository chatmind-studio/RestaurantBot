from typing import Any

from line import Bot, Cog, Context, command
from line.models import ButtonsTemplate, URIAction


class InfoCog(Cog):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    @command
    async def shop_info(self, ctx: Context) -> Any:
        await ctx.reply_template(
            "店家資訊",
            template=ButtonsTemplate(
                title="麥當勞-高雄博愛二餐廳",
                text="地址: 813高雄市左營區博愛三路225號\n營業時間: 7:00~21:30, 週二公休",
                actions=[
                    URIAction(
                        label="Google 地圖", uri="https://goo.gl/maps/YRpkfpQ1C1LEdLew8"
                    ),
                    URIAction(label="致電", uri="tel:073461756"),
                ],
                thumbnail_image_url="https://lh5.googleusercontent.com/p/AF1QipOXKBPpqvEupr_MsCyFiBb6x2kTv6mIJAPu_d79=w408-h306-k-no",
            ),
        )

    @command
    async def reservation(self, ctx: Context) -> Any:
        await ctx.reply_template(
            "訂位",
            template=ButtonsTemplate(
                title="訂位",
                text="目前採電話定位制",
                actions=[
                    URIAction(label="致電", uri="tel:073461756"),
                ],
                thumbnail_image_url="https://lh5.googleusercontent.com/p/AF1QipOXKBPpqvEupr_MsCyFiBb6x2kTv6mIJAPu_d79=w408-h306-k-no",
            ),
        )
