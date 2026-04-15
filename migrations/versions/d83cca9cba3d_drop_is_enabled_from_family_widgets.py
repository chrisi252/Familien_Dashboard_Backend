"""drop_is_enabled_from_family_widgets

Revision ID: d83cca9cba3d
Revises: fe0fda81085d
Create Date: 2026-04-04 18:44:12.466428

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'd83cca9cba3d'
down_revision = 'fe0fda81085d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('family_widgets', schema=None) as batch_op:
        batch_op.drop_column('is_enabled')


def downgrade():
    with op.batch_alter_table('family_widgets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default=sa.text('true')))
