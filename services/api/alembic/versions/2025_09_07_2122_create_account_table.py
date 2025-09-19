"""create_account_table

Revision ID: 3c1d9799f90d
Revises:
Create Date: 2025-09-07 21:22:28.732058

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3c1d9799f90d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "account",
        sa.Column("id", sa.String(24), nullable=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("auth_provider_id", sa.String(255), unique=True, nullable=True),
        sa.Column("auth_provider", sa.String(255), unique=False, nullable=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("picture_url", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("last_login", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("account")
