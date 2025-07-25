"""Rename password_hash to password and add email column

Revision ID: aabf62c75ccb
Revises: d73990ec5a47
Create Date: 2025-07-20 18:43:08.864413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aabf62c75ccb'
down_revision = 'd73990ec5a47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
        batch_op.drop_column('password_hash')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.drop_column('email')
        batch_op.drop_column('password')

    # ### end Alembic commands ###
