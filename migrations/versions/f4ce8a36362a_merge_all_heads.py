"""merge_all_heads

Revision ID: f4ce8a36362a
Revises: a6c723b21481, c3f1a2b4d5e6, ebf78e7d5fcf
Create Date: 2026-03-22 17:16:43.846488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4ce8a36362a'
down_revision = ('a6c723b21481', 'c3f1a2b4d5e6', 'ebf78e7d5fcf')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
