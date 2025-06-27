import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings


class KnowledgeBaseQuerier:
    """Query a pandas-based knowledge base using OpenAI embeddings"""

    def __init__(self, kb_path: str, embedding_model: str = "text-embedding-3-large"):
        self.kb_path = Path(kb_path)
        self.df = None
        self.embeddings = None
        self.embedding_model = OpenAIEmbeddings(model=embedding_model)
        self._load_knowledge_base_flexible()

    def _load_knowledge_base_flexible(self):
        """Load knowledge base with flexible column support"""
        if self.kb_path.exists():
            try:
                # Load the parquet file
                temp_df = pd.read_parquet(self.kb_path)

                # Check what columns are available
                available_cols = set(temp_df.columns)
                required_cols = {"combined_text", "embedding"}
                optional_cols = {"id", "Category_1", "Category_2"}

                if not required_cols.issubset(available_cols):
                    raise ValueError(
                        f"DataFrame must contain at least: {required_cols}"
                    )

                # Use available columns
                cols_to_use = list(
                    required_cols.union(available_cols.intersection(optional_cols))
                )
                self.df = temp_df[cols_to_use].copy()

                # Add missing columns with defaults
                if "id" not in self.df.columns:
                    self.df["id"] = [f"doc_{i}" for i in range(len(self.df))]
                if "Category_1" not in self.df.columns:
                    self.df["Category_1"] = "General"
                if "Category_2" not in self.df.columns:
                    self.df["Category_2"] = "General"

                print(f"  - Knowledge base loaded: {len(self.df)} entries")

                # Convert embeddings to numpy array
                if isinstance(self.df["embedding"].iloc[0], list):
                    self.embeddings = np.vstack(self.df["embedding"].values)
                else:
                    self.embeddings = np.vstack(
                        self.df["embedding"].apply(np.array).values
                    )

                print(f"  - Embeddings shape: {self.embeddings.shape}")

            except Exception as e:
                print(f"  - Error loading knowledge base: {e}")
                self.df = None
                self.embeddings = None
        else:
            print(f"  - Knowledge base not found at: {self.kb_path}")

    def semantic_search(
        self, query_text: str, top_k: int = 10, category_filter: Optional[str] = None
    ) -> List[Dict]:
        """Perform semantic search using OpenAI embeddings"""
        if self.df is None or self.embeddings is None:
            return []

        # Encode the query using OpenAI
        print("  - Encoding query with OpenAI embeddings...")
        query_embedding = self.embedding_model.embed_query(query_text)
        query_embedding = np.array(query_embedding).reshape(1, -1)

        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()

        # Apply category filter if specified
        if category_filter:
            mask = (self.df["Category_1"] == category_filter) | (
                self.df["Category_2"] == category_filter
            )
            filtered_indices = self.df[mask].index
            # Set non-matching indices to -1
            for i in range(len(similarities)):
                if i not in filtered_indices:
                    similarities[i] = -1

        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] < 0.3:  # Skip low similarity results
                continue

            row = self.df.iloc[idx]

            result = {
                "score": float(similarities[idx]),
                "id": row["id"],
                "combined_text": row["combined_text"],
                "category_1": row["Category_1"],
                "category_2": row["Category_2"],
            }

            results.append(result)

        return results

    def search(self, chapter_info: str) -> List[Dict]:
        """Search based on chapter information"""
        # Create a comprehensive query from chapter info

        # Combine into query
        full_query = " ".join(chapter_info)

        # Check if we should filter by category based on chapter keywords (TODO)
        category_filter = None

        return self.semantic_search(full_query, category_filter=None)

    def format_results(self, results: List[Dict]) -> str:
        """Format search results for inclusion in research prompt"""
        if not results:
            return ""

        formatted = "\n\n### Knowledge Base Insights (Semantic Search Results):\n"
        formatted += f"*Found {len(results)} highly relevant entries*\n"

        for i, result in enumerate(results, 1):
            formatted += f"\n**Entry {i}** (Similarity: {result['score']:.3f})\n"
            formatted += f"- ID: {result['id']}\n"
            formatted += f"- Categories: {result['category_1']}"

            if result["category_2"] and result["category_2"] != result["category_1"]:
                formatted += f" > {result['category_2']}"
            formatted += "\n"

            # Include full text for high similarity scores, truncate for lower scores
            text = result["combined_text"]
            if result["score"] > 0.7:
                formatted += f"- Content: {text}\n"
            elif len(text) > 800:
                formatted += f"- Content: {text[:800]}...\n"
            else:
                formatted += f"- Content: {text}\n"

        return formatted
