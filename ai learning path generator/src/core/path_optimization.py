# src/core/path_optimization.py
from sklearn.cluster import KMeans
import numpy as np

class PathOptimizer:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def optimize_learning_sequence(self, topics: List[str]) -> List[str]:
        """Optimize topic sequence using embeddings and clustering"""
        # Generate embeddings
        embeddings = self.embedding_model.encode(topics)
        
        # Cluster topics by similarity
        clusters = KMeans(n_clusters=min(len(topics), 5)).fit_predict(embeddings)
        
        # Order topics within clusters
        return self._order_by_complexity(topics, clusters)