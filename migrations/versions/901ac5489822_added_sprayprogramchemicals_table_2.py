"""Add spray_record_id to spray_program_chemicals and fields to spray_records

Revision ID: 098918ee102a
Revises: d803d4a74b7a
Create Date: 2025-07-01 13:49:19.279215
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# Revision identifiers, used by Alembic.
revision: str = "098918ee102a"
down_revision: Union[str, Sequence[str], None] = "d803d4a74b7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add nullable column first to avoid integrity errors
    op.add_column(
        "spray_program_chemicals",
        sa.Column("spray_record_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "spray_program_chemicals",
        sa.Column("batch_number", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_foreign_key(
        "fk_spray_program_chemicals_spray_record_id",
        "spray_program_chemicals",
        "spray_records",
        ["spray_record_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Add new columns to spray_records
    op.add_column(
        "spray_records",
        sa.Column("date_completed", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "spray_records",
        sa.Column("date_updated", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "spray_records",
        sa.Column("growth_stage_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_spray_records_date_completed",
        "spray_records",
        ["date_completed"],
        unique=False,
    )
    op.create_index(
        "ix_spray_records_date_updated",
        "spray_records",
        ["date_updated"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_spray_records_growth_stage_id",
        "spray_records",
        "growth_stages",
        ["growth_stage_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_spray_records_growth_stage_id", "spray_records", type_="foreignkey"
    )
    op.drop_index("ix_spray_records_date_updated", table_name="spray_records")
    op.drop_index("ix_spray_records_date_completed", table_name="spray_records")
    op.drop_column("spray_records", "growth_stage_id")
    op.drop_column("spray_records", "date_updated")
    op.drop_column("spray_records", "date_completed")

    op.drop_constraint(
        "fk_spray_program_chemicals_spray_record_id",
        "spray_program_chemicals",
        type_="foreignkey",
    )
    op.drop_column("spray_program_chemicals", "batch_number")
    op.drop_column("spray_program_chemicals", "spray_record_id")
