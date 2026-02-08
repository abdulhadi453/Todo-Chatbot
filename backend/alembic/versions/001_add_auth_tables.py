"""Add authentication tables

Revision ID: 001
Revises:
Create Date: 2026-01-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
import uuid

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('disabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create refresh_tokens table
    op.create_table('refreshtoken',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token_hash', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_users_email', 'user', ['email'])
    op.create_index('idx_users_disabled', 'user', ['disabled'])
    op.create_index('idx_refresh_tokens_user_id', 'refreshtoken', ['user_id'])
    op.create_index('idx_refresh_tokens_expires_at', 'refreshtoken', ['expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_refresh_tokens_expires_at', table_name='refreshtoken')
    op.drop_index('idx_refresh_tokens_user_id', table_name='refreshtoken')
    op.drop_index('idx_users_disabled', table_name='user')
    op.drop_index('idx_users_email', table_name='user')

    # Drop tables
    op.drop_table('refreshtoken')
    op.drop_table('user')