"""Add composite index on draw_date and lotto_type_id

Revision ID: a1b2c3d4e5f6
Revises: 969c3033696a
Create Date: 2024-01-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '969c3033696a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add composite index for faster lookups by date and lotto type
    op.create_index(
        'ix_winning_draw_date_lotto_type',
        'winning_draw',
        ['draw_date', 'lotto_type_id'],
        unique=False
    )
    # Add index on lotto_type_id for foreign key lookups
    op.create_index(
        op.f('ix_winning_draw_lotto_type_id'),
        'winning_draw',
        ['lotto_type_id'],
        unique=False
    )
    # Add unique constraint to prevent duplicate draws per date/type
    op.create_unique_constraint(
        'uq_draw_date_lotto_type',
        'winning_draw',
        ['draw_date', 'lotto_type_id']
    )


def downgrade() -> None:
    op.drop_constraint('uq_draw_date_lotto_type', 'winning_draw', type_='unique')
    op.drop_index('ix_winning_draw_date_lotto_type', table_name='winning_draw')
    op.drop_index(op.f('ix_winning_draw_lotto_type_id'), table_name='winning_draw')
