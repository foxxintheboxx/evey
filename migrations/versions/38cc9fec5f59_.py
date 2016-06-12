"""empty message

Revision ID: 38cc9fec5f59
Revises: 7f6a2be96c31
Create Date: 2016-06-12 16:58:37.160074

"""

# revision identifiers, used by Alembic.
revision = '38cc9fec5f59'
down_revision = '7f6a2be96c31'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('message_uid', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('message', 'message_uid')
    ### end Alembic commands ###
