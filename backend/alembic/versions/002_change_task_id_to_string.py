"""Change task ID from integer to string

Revision ID: 002
Revises: 001
Create Date: 2026-01-27 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add a new temporary id column with string type
    op.add_column('todotask', sa.Column('new_id', sa.String(), nullable=True))

    # Update the new_id column with string representations of existing integer IDs
    # For new records, we'll use UUIDs
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT id FROM todotask"))
    rows = res.fetchall()

    for row in rows:
        # Convert existing integer IDs to string (we'll keep them as string numbers for now)
        conn.execute(
            sa.text("UPDATE todotask SET new_id = :new_id WHERE id = :old_id"),
            {"new_id": str(row[0]), "old_id": row[0]}
        )

    # Make the new_id column non-nullable
    op.alter_column('todotask', 'new_id', nullable=False)

    # Drop the old id column
    op.drop_column('todotask', 'id')

    # Rename the new_id column to id
    op.alter_column('todotask', 'new_id', new_column_name='id')

    # Recreate the primary key constraint
    op.create_primary_key('pk_todotask', 'todotask', ['id'])


def downgrade():
    # Add a temporary integer id column
    op.add_column('todotask', sa.Column('temp_id', sa.Integer(), nullable=True))

    # Update temp_id with integer representations of existing string IDs (where possible)
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT id FROM todotask"))
    rows = res.fetchall()

    for row in rows:
        try:
            # Try to convert string ID back to integer
            int_id = int(row[0])
            conn.execute(
                sa.text("UPDATE todotask SET temp_id = :int_id WHERE id = :str_id"),
                {"int_id": int_id, "str_id": row[0]}
            )
        except ValueError:
            # If conversion fails, assign a new integer ID (this is a limitation of the downgrade)
            print(f"Warning: Could not convert ID '{row[0]}' back to integer for downgrade.")

    # Make temp_id non-nullable
    op.alter_column('todotask', 'temp_id', nullable=False)

    # Drop the old id column
    op.drop_column('todotask', 'id')

    # Rename temp_id to id
    op.alter_column('todotask', 'temp_id', new_column_name='id')

    # Recreate the primary key constraint
    op.create_primary_key('pk_todotask', 'todotask', ['id'])