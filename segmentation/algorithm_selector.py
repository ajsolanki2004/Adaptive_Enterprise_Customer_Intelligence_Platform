from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score

class AlgorithmSelector:
    """
    Utility to evaluate and choose between different clustering algorithmic families.
    """
    @staticmethod
    def select_best_algorithm(data, n_clusters=3):
        algorithms = {
            "KMeans": KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
            "Agglomerative": AgglomerativeClustering(n_clusters=n_clusters)
        }
        
        best_algo = None
        best_score = -1
        
        for name, model in algorithms.items():
            labels = model.fit_predict(data)
            score = silhouette_score(data, labels)
            print(f"{name} silhouette score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_algo = name
                
        print(f"Best algorithm selected: {best_algo}")
        return best_algo
