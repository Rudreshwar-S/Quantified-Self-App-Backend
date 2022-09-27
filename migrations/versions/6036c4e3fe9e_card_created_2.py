"""Card Created 2.

Revision ID: 6036c4e3fe9e
Revises: 9d8aa09b1722
Create Date: 2022-09-28 00:10:59.670159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6036c4e3fe9e'
down_revision = '9d8aa09b1722'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('time_stamp', sa.String(length=50), nullable=True))
    op.create_unique_constraint(None, 'card', ['time_stamp'])
    op.drop_column('card', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('name', sa.VARCHAR(length=50), nullable=True))
    op.drop_constraint(None, 'card', type_='unique')
    op.drop_column('card', 'time_stamp')
    # ### end Alembic commands ###