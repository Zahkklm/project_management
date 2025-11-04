"""add_email_to_user

Revision ID: add_email_to_user
Revises: b503171e1db5
Create Date: 2025-01-04

"""

import sqlalchemy as sa

from alembic import op  # type: ignore

revision = "add_email_to_user"
down_revision = "b503171e1db5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "email")
