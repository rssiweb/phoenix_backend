"""empty message

Revision ID: ee2a82e56012
Revises: 9868f58df3cb
Create Date: 2018-03-04 15:05:39.311036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee2a82e56012'
down_revision = '9868f58df3cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('faculty', sa.Column('isActive', sa.Boolean(), nullable=True))
    op.add_column('student', sa.Column('isActive', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student', 'isActive')
    op.drop_column('faculty', 'isActive')
    # ### end Alembic commands ###