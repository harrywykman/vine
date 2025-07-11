"""Added target row to Chemicals

Revision ID: 617fb7736122
Revises: 739ccae07c79
Create Date: 2025-06-26 12:50:45.113656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '617fb7736122'
down_revision: Union[str, Sequence[str], None] = '739ccae07c79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_created_date'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_last_login'), table_name='users')
    op.drop_table('users')
    op.add_column('chemicals', sa.Column('target', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('chemicals', 'status')
    sa.Enum('OPEN', 'CLOSED', name='taskstatus').drop(op.get_bind())
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('OPEN', 'CLOSED', name='taskstatus').create(op.get_bind())
    op.add_column('chemicals', sa.Column('status', postgresql.ENUM('OPEN', 'CLOSED', name='taskstatus', create_type=False), autoincrement=False, nullable=True))
    op.drop_column('chemicals', 'target')
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hash_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('last_login', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('users_pkey'))
    )
    op.create_index(op.f('ix_users_last_login'), 'users', ['last_login'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_created_date'), 'users', ['created_date'], unique=False)
    # ### end Alembic commands ###
