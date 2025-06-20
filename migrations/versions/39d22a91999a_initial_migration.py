"""Initial migration

Revision ID: 39d22a91999a
Revises: 
Create Date: 2025-06-03 11:10:55.881578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39d22a91999a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('user_learning_paths',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('path_data_json', sa.JSON(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('topic', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
    sa.Column('is_archived', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user_learning_paths', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_learning_paths_created_at'), ['created_at'], unique=False)

    op.create_table('learning_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_learning_path_id', sa.String(length=36), nullable=False),
    sa.Column('milestone_identifier', sa.String(length=200), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_learning_path_id'], ['user_learning_paths.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_learning_path_id', 'milestone_identifier', name='_user_path_milestone_uc')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('learning_progress')
    with op.batch_alter_table('user_learning_paths', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_learning_paths_created_at'))

    op.drop_table('user_learning_paths')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    # ### end Alembic commands ###
