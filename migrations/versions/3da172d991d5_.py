"""empty message

Revision ID: 3da172d991d5
Revises: ee2a82e56012
Create Date: 2018-03-05 11:32:38.883134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3da172d991d5'
down_revision = 'ee2a82e56012'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('attendance', 'punch_in',
               existing_type=sa.TEXT(length=50),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('attendance', 'punch_in',
               existing_type=sa.TEXT(length=50),
               nullable=False)
    # ### end Alembic commands ###
