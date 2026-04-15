"""user_widget_configs

Revision ID: a9f3c2b1e4d7
Revises: d83cca9cba3d
Create Date: 2026-04-05 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a9f3c2b1e4d7'
down_revision = 'd83cca9cba3d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_widget_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('family_widget_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('grid_col', sa.Integer(), nullable=False),
        sa.Column('grid_row', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['family_widget_id'], ['family_widgets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'family_widget_id', name='uq_user_widget_config'),
    )

    with op.batch_alter_table('family_widgets', schema=None) as batch_op:
        batch_op.drop_column('grid_col')
        batch_op.drop_column('grid_row')
        batch_op.drop_column('grid_pos_x')
        batch_op.drop_column('grid_pos_y')


def downgrade():
    with op.batch_alter_table('family_widgets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('grid_pos_y', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('grid_pos_x', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('grid_row', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('grid_col', sa.Integer(), nullable=True))

    op.drop_table('user_widget_configs')
