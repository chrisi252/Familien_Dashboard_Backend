"""add family_invite_codes table

Revision ID: 55b7002da431
Revises: ca8592eefde6
Create Date: 2026-04-12 14:08:44.335341

"""
import sqlalchemy as sa
from alembic import op

revision = '55b7002da431'
down_revision = 'ca8592eefde6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('family_invite_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=6), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('family_id')
    )
    with op.batch_alter_table('family_invite_codes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_family_invite_codes_code'), ['code'], unique=True)


def downgrade():
    with op.batch_alter_table('family_invite_codes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_family_invite_codes_code'))
    op.drop_table('family_invite_codes')
