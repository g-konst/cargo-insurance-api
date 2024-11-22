"""add modified_at column to cargo_rates

Revision ID: 999cf6d2695c
Revises: 23ee408530c7
Create Date: 2024-11-22 18:22:19.835985

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "999cf6d2695c"
down_revision: Union[str, None] = "23ee408530c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cargo_rates",
        sa.Column(
            "modified_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("cargo_rates", "modified_at")
