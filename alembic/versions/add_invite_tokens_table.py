"""Add invite_tokens table

Revision ID: add_invite_tokens
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "add_invite_tokens"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create invite_tokens table."""
    op.create_table(
        "invite_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_invite_tokens_id"), "invite_tokens", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_invite_tokens_token"),
        "invite_tokens",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    """Drop invite_tokens table."""
    op.drop_index(op.f("ix_invite_tokens_token"), table_name="invite_tokens")
    op.drop_index(op.f("ix_invite_tokens_id"), table_name="invite_tokens")
    op.drop_table("invite_tokens")
