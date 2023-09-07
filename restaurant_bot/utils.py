import base64
import datetime
import io
from typing import List, TypeVar

import aiohttp
from PIL.Image import Image

T = TypeVar("T")


def split_list(input_list: List[T], n: int) -> List[List[T]]:
    """
    Split a list into sublists of length n

    Parameters:
        input_list: The input list
        n: The length of each sublist
    """
    if n <= 0:
        raise ValueError("Parameter n must be a positive integer")

    return [input_list[i : i + n] for i in range(0, len(input_list), n)]


async def upload_image(image: Image) -> str:
    # encode image to base64 string
    bytes_io = io.BytesIO()
    image.save(bytes_io, format="PNG")
    bytes_io.seek(0)
    image_bytes = bytes_io.read()
    base64_string = base64.b64encode(image_bytes).decode("ascii")
    data = {
        "key": "6d207e02198a847aa98d0a2a901485a5",
        "source": base64_string,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://freeimage.host/api/1/upload", data=data
        ) as resp:
            return (await resp.json())["image"]["url"]


def get_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
