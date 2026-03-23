"""initial schema

Revision ID: 38be89c9f3af
Revises: 
Create Date: 2026-03-18 11:49:19.472710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '38be89c9f3af'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('position', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('applied_date', sa.Date(), nullable=True),
        sa.Column('job_url', sa.String(length=1000), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_company'), 'applications', ['company'], unique=False)
    op.create_index(op.f('ix_applications_status'), 'applications', ['status'], unique=False)

    op.create_table(
        'application_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('old_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('gmail_message_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_events_application_id'), 'application_events', ['application_id'], unique=False)
    op.create_index(op.f('ix_application_events_event_type'), 'application_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_application_events_gmail_message_id'), 'application_events', ['gmail_message_id'], unique=False)
    op.create_index(op.f('ix_application_events_id'), 'application_events', ['id'], unique=False)
    op.create_index(op.f('ix_application_events_source'), 'application_events', ['source'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_application_events_source'), table_name='application_events')
    op.drop_index(op.f('ix_application_events_id'), table_name='application_events')
    op.drop_index(op.f('ix_application_events_gmail_message_id'), table_name='application_events')
    op.drop_index(op.f('ix_application_events_event_type'), table_name='application_events')
    op.drop_index(op.f('ix_application_events_application_id'), table_name='application_events')
    op.drop_table('application_events')

    op.drop_index(op.f('ix_applications_status'), table_name='applications')
    op.drop_index(op.f('ix_applications_company'), table_name='applications')
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    op.drop_table('applications')