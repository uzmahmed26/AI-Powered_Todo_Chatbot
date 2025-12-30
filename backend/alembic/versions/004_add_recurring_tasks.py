"""add recurring tasks support

Revision ID: 004
Revises: 003
Create Date: 2025-12-30
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add recurring tasks fields to tasks table."""

    # Add is_recurring flag
    op.add_column(
        'tasks',
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false')
    )

    # Add recurrence_pattern (daily, weekly, monthly)
    op.add_column(
        'tasks',
        sa.Column('recurrence_pattern', sa.String(length=20), nullable=True)
    )

    # Add recurrence_interval (default 1)
    op.add_column(
        'tasks',
        sa.Column('recurrence_interval', sa.Integer(), nullable=False, server_default='1')
    )

    # Add recurrence_end_date (optional)
    op.add_column(
        'tasks',
        sa.Column('recurrence_end_date', sa.DateTime(timezone=True), nullable=True)
    )

    # Add recurrence_day_of_week (0-6 for weekly, 0=Monday)
    op.add_column(
        'tasks',
        sa.Column('recurrence_day_of_week', sa.Integer(), nullable=True)
    )

    # Add recurrence_day_of_month (1-31 for monthly)
    op.add_column(
        'tasks',
        sa.Column('recurrence_day_of_month', sa.Integer(), nullable=True)
    )

    # Add parent_recurrence_id (links to original recurring task)
    op.add_column(
        'tasks',
        sa.Column('parent_recurrence_id', sa.Integer(), nullable=True)
    )

    # Add recurrence_active flag (can pause/resume)
    op.add_column(
        'tasks',
        sa.Column('recurrence_active', sa.Boolean(), nullable=False, server_default='true')
    )

    # Create indexes for performance
    op.create_index('idx_task_is_recurring', 'tasks', ['is_recurring'])
    op.create_index('idx_task_recurrence_active', 'tasks', ['recurrence_active'])
    op.create_index('idx_task_parent_recurrence', 'tasks', ['parent_recurrence_id'])

    # Add foreign key for parent_recurrence_id (self-referencing)
    op.create_foreign_key(
        'fk_task_parent_recurrence',
        'tasks',
        'tasks',
        ['parent_recurrence_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Remove recurring tasks fields."""

    # Drop foreign key
    op.drop_constraint('fk_task_parent_recurrence', 'tasks', type_='foreignkey')

    # Drop indexes
    op.drop_index('idx_task_parent_recurrence', table_name='tasks')
    op.drop_index('idx_task_recurrence_active', table_name='tasks')
    op.drop_index('idx_task_is_recurring', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'recurrence_active')
    op.drop_column('tasks', 'parent_recurrence_id')
    op.drop_column('tasks', 'recurrence_day_of_month')
    op.drop_column('tasks', 'recurrence_day_of_week')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')
