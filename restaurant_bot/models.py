from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class Coupon(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20)
    description = fields.CharField(max_length=100)
    expire_date = fields.DateField()
    users: fields.ManyToManyRelation["User"]


class User(Model):
    id = fields.CharField(pk=True, max_length=33)
    name = fields.CharField(max_length=255)
    points = fields.IntField(default=0, min_value=0)
    coupons: fields.ManyToManyRelation[Coupon] = fields.ManyToManyField(
        "models.Coupon", related_name="users", through="user_coupon"
    )
    is_admin = fields.BooleanField(default=False)
    password = fields.CharField(max_length=255, null=True, default=None)


class ItemCategory(StrEnum):
    FOOD = "食物"
    DRINK = "飲料"
    DESSERT = "甜點"
    APPETIZER = "開胃菜"


class Item(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20)
    description = fields.CharField(max_length=50)
    category = fields.CharEnumField(ItemCategory, max_length=20)
    price = fields.IntField(min_value=0)
    image_url = fields.CharField(max_length=255, null=True, default=None)
