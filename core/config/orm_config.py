from contextvars import ContextVar

import peewee
from fastapi import Depends
from playhouse.pool import PooledPostgresqlExtDatabase

from core.config.var_config import (
    IS_PROD,
    DB_NAME,
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
)

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


if IS_PROD:
    db = PooledPostgresqlExtDatabase(
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        max_connections=8,
        stale_timeout=300,
    )
    db.set_time_zone("Asia/Seoul")
else:
    from core.config import secrets

    db = PooledPostgresqlExtDatabase(
        database=DB_NAME,
        host=secrets.DB_HOST,
        port=secrets.DB_PORT,
        user=secrets.DB_USER,
        password=secrets.DB_PASSWORD,
        max_connections=8,
        stale_timeout=300,
    )
    db.set_time_zone("Asia/Seoul")
db._state = PeeweeConnectionState()


async def reset_db_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def read_only(db_state=Depends(reset_db_state)):
    try:
        db.connect()
        yield
    finally:
        if not db.is_closed():
            db.close()


def transactional(db_state=Depends(reset_db_state)):
    try:
        db.connect()
        with db.transaction() as txn:
            yield
            txn.commit()
    except Exception as e:
        txn.rollback()
        raise e
    finally:
        if not db.is_closed():
            db.close()
