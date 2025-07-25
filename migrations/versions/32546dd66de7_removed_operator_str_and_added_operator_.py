"""removed operator str and added operator_id to SprayRecord

Revision ID: 32546dd66de7
Revises: 9cf5593a027e
Create Date: 2025-07-17 14:12:47.565994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '32546dd66de7'
down_revision: Union[str, Sequence[str], None] = '9cf5593a027e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
