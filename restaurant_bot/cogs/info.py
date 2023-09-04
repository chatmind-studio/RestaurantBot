from typing import Any

from line import Bot, Cog, Context, command
from line.models import ButtonsTemplate, URIAction


class InfoCog(Cog):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    @command
    async def shop_info(self, ctx: Context) -> Any:
        await ctx.reply_template(
            alt_text="店家資訊",
            template=ButtonsTemplate(
                title="丹丹漢堡 (文慈店)",
                text="地址: 813高雄市左營區文慈路192-1號\n營業時間: 7:00~21:30, 週二公休",
                actions=[
                    URIAction(
                        label="Google 地圖", uri="https://goo.gl/maps/bLTS7sFZhe2TRr9D9"
                    ),
                    URIAction(label="致電", uri="tel:073469388"),
                ],
                thumbnail_image_url="https://lh5.googleusercontent.com/p/AF1QipMQXLxVJkpAFG5A3T0oRSFOpsdOLdzdPdaAZ2_c=w408-h306-k-no",
            ),
        )
