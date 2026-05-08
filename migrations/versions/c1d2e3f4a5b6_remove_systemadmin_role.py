"""remove_systemadmin_role

Die 'Systemadmin'-Rolle in der roles-Tabelle wurde nie über UserFamilyRole vergeben
und ist redundant — der globale Admin-Status wird ausschließlich über
User.is_system_admin verwaltet.

Revision ID: c1d2e3f4a5b6
Revises: b72749c96ed6
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op

revision = 'c1d2e3f4a5b6'
down_revision = 'b72749c96ed6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM roles WHERE name = 'Systemadmin'")


def downgrade():
    op.execute("INSERT INTO roles (name) VALUES ('Systemadmin') ON CONFLICT (name) DO NOTHING")
