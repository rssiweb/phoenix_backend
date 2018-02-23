"""empty message

Revision ID: fa4f8531db8c
Revises: 4519f58b98f5
Create Date: 2018-02-24 01:29:56.476914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa4f8531db8c'
down_revision = '4519f58b98f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subject')
    op.add_column('attendance', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('student', sa.Column('branch', sa.String(length=50), nullable=False))
    op.add_column('student', sa.Column('contact', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student', 'contact')
    op.drop_column('student', 'branch')
    op.drop_column('attendance', 'location')
    op.create_table('subject',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.Column('date_modified', sa.DATETIME(), nullable=True),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###