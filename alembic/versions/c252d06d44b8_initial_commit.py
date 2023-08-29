"""initial commit

Revision ID: c252d06d44b8
Revises:
Create Date: 2023-08-26 20:45:50.251680

"""
from typing import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c252d06d44b8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "dofi_package",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("local_version", sa.String(length=17), nullable=False),
        sa.Column("remote_version", sa.String(length=17), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dofi_package_id"), "dofi_package", ["id"], unique=False)
    op.create_index(op.f("ix_dofi_package_name"), "dofi_package", ["name"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_dofi_package_name"), table_name="dofi_package")
    op.drop_index(op.f("ix_dofi_package_id"), table_name="dofi_package")
    op.drop_table("dofi_package")
    # ### end Alembic commands ###