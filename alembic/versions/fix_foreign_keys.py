"""fix_foreign_keys

Revision ID: fix_foreign_keys
Revises: add_email_to_user
Create Date: 2025-01-04

"""

import sqlalchemy as sa

from alembic import op  # type: ignore

revision = "fix_foreign_keys"
down_revision = "add_email_to_user"
branch_labels = None
depends_on = None


def upgrade():
    # Drop bad foreign key if exists
    op.execute(
        "ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_owner_id_fkey"
    )
    # Add correct foreign key
    op.create_foreign_key(
        "projects_owner_id_fkey",
        "projects",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(
        "projects_owner_id_fkey", "projects", type_="foreignkey"
    )
