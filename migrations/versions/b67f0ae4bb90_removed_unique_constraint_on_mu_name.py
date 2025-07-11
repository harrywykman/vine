"""removed unique constraint on mu name

Revision ID: b67f0ae4bb90
Revises: 82bcde2beb5f
Create Date: 2025-07-02 16:26:03.608021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b67f0ae4bb90'
down_revision: Union[str, Sequence[str], None] = '82bcde2beb5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('chemical_group_link_group_id_fkey'), 'chemical_group_link', type_='foreignkey')
    op.drop_constraint(op.f('chemical_group_link_chemical_id_fkey'), 'chemical_group_link', type_='foreignkey')
    op.create_foreign_key(None, 'chemical_group_link', 'chemicals', ['chemical_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'chemical_group_link', 'chemical_groups', ['group_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_management_units_name'), table_name='management_units')
    op.create_index(op.f('ix_management_units_name'), 'management_units', ['name'], unique=False)
    op.drop_constraint(op.f('management_units_vineyard_id_fkey'), 'management_units', type_='foreignkey')
    op.create_foreign_key(None, 'management_units', 'vineyards', ['vineyard_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_spray_records_management_unit_id'), 'spray_records', ['management_unit_id'], unique=False)
    op.create_index(op.f('ix_spray_records_spray_program_id'), 'spray_records', ['spray_program_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_spray_records_spray_program_id'), table_name='spray_records')
    op.drop_index(op.f('ix_spray_records_management_unit_id'), table_name='spray_records')
    op.drop_constraint(None, 'management_units', type_='foreignkey')
    op.create_foreign_key(op.f('management_units_vineyard_id_fkey'), 'management_units', 'vineyards', ['vineyard_id'], ['id'])
    op.drop_index(op.f('ix_management_units_name'), table_name='management_units')
    op.create_index(op.f('ix_management_units_name'), 'management_units', ['name'], unique=True)
    op.drop_constraint(None, 'chemical_group_link', type_='foreignkey')
    op.drop_constraint(None, 'chemical_group_link', type_='foreignkey')
    op.create_foreign_key(op.f('chemical_group_link_chemical_id_fkey'), 'chemical_group_link', 'chemicals', ['chemical_id'], ['id'])
    op.create_foreign_key(op.f('chemical_group_link_group_id_fkey'), 'chemical_group_link', 'chemical_groups', ['group_id'], ['id'])
    # ### end Alembic commands ###
