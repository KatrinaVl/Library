"""Rename table users to readers

Revision ID: 3381f67a3256
Revises: 0212b2f72dd6
Create Date: 2025-05-20 20:33:51.173857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3381f67a3256'
down_revision: Union[str, None] = '0212b2f72dd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.rename_table('users', 'readers')


def downgrade():
    op.rename_table('readers', 'users')
