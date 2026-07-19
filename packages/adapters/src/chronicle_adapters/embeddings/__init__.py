"""Embedding adapters re-export application hashing embedder for infra wiring."""

from chronicle_application.embeddings import HashingEmbedder, cosine_similarity

__all__ = ["HashingEmbedder", "cosine_similarity"]
