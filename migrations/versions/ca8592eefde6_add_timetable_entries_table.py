"""add timetable_entries table

Revision ID: ca8592eefde6
Revises: b1c2d3e4f5a6
Create Date: 2026-04-12 13:50:17.538397

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ca8592eefde6'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('timetable_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=False),
    sa.Column('person_name', sa.String(length=100), nullable=False),
    sa.Column('color', sa.String(length=7), nullable=False),
    sa.Column('weekday', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.String(length=5), nullable=False),
    sa.Column('end_time', sa.String(length=5), nullable=False),
    sa.Column('subject', sa.String(length=100), nullable=False),
    sa.Column('room', sa.String(length=50), nullable=True),
    sa.Column('teacher', sa.String(length=100), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint('weekday >= 0 AND weekday <= 4', name='ck_timetable_weekday'),
    sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('timetable_entries')
