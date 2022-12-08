"""empty message

Revision ID: 8ebaaba69488
Revises: d62e27032709
Create Date: 2018-05-26 03:18:54.550060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ebaaba69488'
down_revision = 'd62e27032709'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('test', sa.Column('max_marks', sa.Integer(), nullable=False))
    op.alter_column('test', 'date',
               existing_type=sa.DATE(),
               nullable=False)
    op.create_unique_constraint('testcode_in_exam_uc', 'test', ['name', 'exam_id'])
    op.drop_index('name', table_name='test')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('name', 'test', ['name'], unique=True)
    op.drop_constraint('testcode_in_exam_uc', 'test', type_='unique')
    op.alter_column('test', 'date',
               existing_type=sa.DATE(),
               nullable=True)
    op.drop_column('test', 'max_marks')
    # ### end Alembic commands ###