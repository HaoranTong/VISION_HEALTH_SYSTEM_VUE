"""Initial migration

Revision ID: ff6682b2db83
Revises: 
Create Date: 2025-02-13 11:14:46.332258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff6682b2db83'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_edu_id', sa.String(length=20), nullable=True),
    sa.Column('school_code', sa.String(length=6), nullable=False),
    sa.Column('school_id', sa.String(length=20), nullable=True),
    sa.Column('index_id', sa.String(length=40), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('vision_left', sa.Float(), nullable=False),
    sa.Column('vision_right', sa.Float(), nullable=False),
    sa.Column('myopia_level', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('index_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students')
    # ### end Alembic commands ###
