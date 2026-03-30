"""Add family_weather_configs table

Revision ID: c3f1a2b4d5e6
Revises: 71512365238e
Create Date: 2026-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f1a2b4d5e6'
down_revision = '71512365238e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'family_weather_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('city_name', sa.String(length=255), nullable=False, server_default='Berlin'),
        sa.Column('latitude', sa.Float(), nullable=False, server_default='52.52'),
        sa.Column('longitude', sa.Float(), nullable=False, server_default='13.405'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('family_id')
    )


def downgrade():
    op.drop_table('family_weather_configs')
