"""empty message

Revision ID: b99ff7b0224b
Revises: 4db31a3dbef9
Create Date: 2018-02-25 16:19:23.163624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b99ff7b0224b'
down_revision = '4db31a3dbef9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attendance', sa.Column('punch_in', sa.String(length=50), nullable=False))
    op.add_column('attendance', sa.Column('punch_in_by_id', sa.Integer(), nullable=True))
    op.add_column('attendance', sa.Column('punch_out', sa.String(length=50), nullable=True))
    op.add_column('attendance', sa.Column('punch_out_by_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'attendance', 'faculty', ['punch_in_by_id'], ['id'])
    op.create_foreign_key(None, 'attendance', 'faculty', ['punch_out_by_id'], ['id'])
    op.drop_column('attendance', 'punchIn')
    op.drop_column('attendance', 'punchOut')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attendance', sa.Column('punchOut', sa.NUMERIC(precision=50), nullable=True))
    op.add_column('attendance', sa.Column('punchIn', sa.TEXT(length=50), nullable=False))
    op.drop_constraint(None, 'attendance', type_='foreignkey')
    op.drop_constraint(None, 'attendance', type_='foreignkey')
    op.drop_column('attendance', 'punch_out_by_id')
    op.drop_column('attendance', 'punch_out')
    op.drop_column('attendance', 'punch_in_by_id')
    op.drop_column('attendance', 'punch_in')
    # ### end Alembic commands ###