"""change embedding dimension to 384

Revision ID: 6701a427af5e
Revises: 96f78e652ecd
Create Date: 2026-03-20 23:58:44.050710

"""
from typing import Sequence, Union

from alembic import op
import pgvector.sqlalchemy.vector
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6701a427af5e'
down_revision: Union[str, Sequence[str], None] = '96f78e652ecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('embeddings', 'embedding')
    op.add_column('embeddings', sa.Column(
        'embedding',
        pgvector.sqlalchemy.vector.VECTOR(dim=384),
        nullable=False,
    ))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('embeddings', 'embedding')
    op.add_column('embeddings', sa.Column(
        'embedding',
        pgvector.sqlalchemy.vector.VECTOR(dim=1536),
        nullable=False,
    ))
