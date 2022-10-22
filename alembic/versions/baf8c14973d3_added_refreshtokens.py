"""added RefreshTokens

Revision ID: baf8c14973d3
Revises: 
Create Date: 2022-10-20 09:28:32.905811

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'baf8c14973d3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'refresh_tokens',
            sa.Column('id', sa.Text(length=100), primary_key=True, default=str(uuid.uuid1()), unique=True, nullable=False),
            sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id")),
            sa.Column('refresh_token',sa.Text(length=100), nullable=False),
            sa.Column('token_expiration_date', sa.DateTime(timezone=True))
    )


def downgrade() -> None:
    pass
