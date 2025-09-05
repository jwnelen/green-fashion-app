"""Add a column

Revision ID: 7468af573b4c
Revises: 2f1010d1df52
Create Date: 2025-09-05 15:33:40.721461

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7468af573b4c"
down_revision: Union[str, Sequence[str], None] = "2f1010d1df52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove description column (not needed for user accounts)
    op.drop_column("account", "description")

    # Add UserResponse fields
    op.add_column(
        "account", sa.Column("google_id", sa.String(255), unique=True, nullable=False)
    )
    op.add_column(
        "account", sa.Column("email", sa.String(255), unique=True, nullable=False)
    )
    op.add_column("account", sa.Column("picture", sa.Text, nullable=True))

    # Add timestamp fields
    op.add_column(
        "account",
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
    )
    op.add_column("account", sa.Column("last_login", sa.DateTime, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop added timestamp fields
    op.drop_column("account", "last_login")
    op.drop_column("account", "created_at")

    # Drop UserResponse fields
    op.drop_column("account", "picture")
    op.drop_column("account", "email")
    op.drop_column("account", "google_id")

    # Re-add description column that was removed
    op.add_column("account", sa.Column("description", sa.Unicode(200), nullable=True))
