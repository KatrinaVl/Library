"""Add column count in Readers

Revision ID: 8ddba7315463
Revises: 9288ede1c34a
Create Date: 2025-05-20 22:01:44.821548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ddba7315463'
down_revision: Union[str, None] = '9288ede1c34a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('readers', sa.Column('count', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('readers', 'count')
