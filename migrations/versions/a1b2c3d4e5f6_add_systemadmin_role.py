"""seed_default_roles

Revision ID: a1b2c3d4e5f6
Revises: d83cca9cba3d
Create Date: 2026-04-04 19:30:00.000000

"""
from alembic import op

revision = 'a1b2c3d4e5f6'
down_revision = 'd83cca9cba3d'
branch_labels = None
depends_on = None


def upgrade():
    for role in ('Familyadmin', 'Guest', 'Systemadmin'):
        op.execute(
            f"INSERT INTO roles (name) VALUES ('{role}') ON CONFLICT (name) DO NOTHING"
        )


def downgrade():
    op.execute("DELETE FROM roles WHERE name IN ('Familyadmin', 'Guest', 'Systemadmin')")
