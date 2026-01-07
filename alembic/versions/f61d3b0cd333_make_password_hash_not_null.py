"""make password_hash not null

Revision ID: f61d3b0cd333
Revises: 09da6c5f017f
Create Date: 2026-01-07 11:13:38.031588

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f61d3b0cd333"
down_revision: Union[str, Sequence[str], None] = "09da6c5f017f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite no soporta ALTER COLUMN para cambiar nullable
    # Usamos batch_alter_table que recrea la tabla
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash", existing_type=sa.String(length=255), nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "password_hash", existing_type=sa.String(length=255), nullable=True
        )
