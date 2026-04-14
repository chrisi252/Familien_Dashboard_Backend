"""drop unused calendar tables

Revision ID: e1a2b3c4d5f6
Revises: 55b7002da431
Create Date: 2026-04-14

"""
from alembic import op
import sqlalchemy as sa


revision = 'e1a2b3c4d5f6'
down_revision = '55b7002da431'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('calendar_event_visibility')
    op.drop_table('calendar_events')


def downgrade():
    op.create_table('calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_datetime', sa.DateTime(), nullable=False),
        sa.Column('end_datetime', sa.DateTime(), nullable=True),
        sa.Column('is_all_day', sa.Boolean(), nullable=True),
        sa.Column('is_public_to_family', sa.Boolean(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('calendar_event_visibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_event_user_visibility'),
    )
