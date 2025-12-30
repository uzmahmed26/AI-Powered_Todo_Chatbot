"""add task enhancements: priority, category, due_date

Revision ID: 003
Revises: 002
Create Date: 2025-12-30
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add priority, category, and due_date columns to tasks table."""

    # Add priority column with default 'medium'
    op.add_column(
        'tasks',
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium')
    )

    # Add category column (nullable)
    op.add_column(
        'tasks',
        sa.Column('category', sa.String(length=50), nullable=True)
    )

    # Add due_date column (nullable)
    op.add_column(
        'tasks',
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True)
    )

    # Create indexes for performance
    op.create_index('idx_task_priority', 'tasks', ['priority'])
    op.create_index('idx_task_category', 'tasks', ['category'])
    op.create_index('idx_task_due_date', 'tasks', ['due_date'])

    # Create composite index for common query pattern
    op.create_index(
        'idx_task_user_status_priority',
        'tasks',
        ['user_id', 'completed', 'priority']
    )


def downgrade() -> None:
    """Remove priority, category, and due_date columns."""

    # Drop indexes
    op.drop_index('idx_task_user_status_priority', table_name='tasks')
    op.drop_index('idx_task_due_date', table_name='tasks')
    op.drop_index('idx_task_category', table_name='tasks')
    op.drop_index('idx_task_priority', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'category')
    op.drop_column('tasks', 'priority')
