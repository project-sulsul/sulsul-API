from enum import Enum

import peewee
from playhouse.postgres_ext import BinaryJSONField

from core.domain.base_entity import BaseEntity


class UserStatus(Enum):
    BAN = "banned"
    ACTIVE = "active"


class User(BaseEntity):
    uid = peewee.CharField(max_length=100, null=False, unique=True)
    social_type = peewee.CharField(max_length=10, null=True)
    nickname = peewee.CharField(max_length=30, null=True)
    image = peewee.CharField(null=True, default=None)
    preference = BinaryJSONField(default={})
    status = peewee.CharField(max_length=10, default=UserStatus.ACTIVE.value)
    device_type = peewee.CharField(null=True)
    push_token = peewee.CharField(null=True)

    class Meta:
        table_name = "user"

    def __getitem__(self, key: str):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = value
