"""Add pgvector embeddings and API credentials."""

from __future__ import annotations

revision = "0002_pgvector_auth"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("memory_chunks", sa.Column("model_id", sa.String(length=64), nullable=True))
    op.execute("ALTER TABLE memory_chunks ADD COLUMN IF NOT EXISTS embedding vector(384)")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_memory_chunks_embedding_hnsw
        ON memory_chunks
        USING hnsw (embedding vector_cosine_ops)
        """
    )
    op.create_table(
        "credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_credentials_workspace_id", "credentials", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_credentials_workspace_id", table_name="credentials")
    op.drop_table("credentials")
    op.execute("DROP INDEX IF EXISTS ix_memory_chunks_embedding_hnsw")
    op.execute("ALTER TABLE memory_chunks DROP COLUMN IF EXISTS embedding")
    op.drop_column("memory_chunks", "model_id")
