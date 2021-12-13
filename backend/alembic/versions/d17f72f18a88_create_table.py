"""Create table

Revision ID: d17f72f18a88
Revises: 
Create Date: 2021-12-13 12:16:54.682681

"""
from alembic import op
import sqlalchemy as sa


revision = "d17f72f18a88"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=True),
        sa.Column("email", sa.String(length=50), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("image", sa.String(length=250), nullable=True),
        sa.Column("password", sa.String(length=250), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("token"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "followers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user", sa.String(length=50), nullable=True),
        sa.Column("author", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["author"], ["users.username"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "article_tag",
        sa.Column("article_id", sa.Integer(), nullable=True),
        sa.Column("tags_name", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tags_name"], ["tags.name"], ondelete="CASCADE"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("author", sa.Integer(), nullable=True),
        sa.Column("article", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["article"], ["articles.slug"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user", sa.String(length=50), nullable=True),
        sa.Column("article", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["article"], ["articles.slug"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_article",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("article_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )


def downgrade():
    op.drop_table("user_article")
    op.drop_table("favorites")
    op.drop_table("comments")
    op.drop_table("article_tag")
    op.drop_table("followers")
    op.drop_table("articles")
    op.drop_table("users")
    op.drop_table("tags")
