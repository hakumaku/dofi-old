from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from dofi.database import ModelBase


class Package(ModelBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=20), index=True, nullable=False)
    # There's a possibility it could be longer than 17, but I don't expect that to be common.
    local_version: Mapped[int] = mapped_column(String(length=17), nullable=False)
    remote_version: Mapped[int] = mapped_column(String(length=17), nullable=False)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
