import numpy as np
from typing import List, Dict

class AHPProcessor:
    def __init__(self, rankings: List[int]):
        self.rankings = rankings
        self.num_criteria = len(rankings)
        if self.num_criteria == 0:
            raise ValueError("Ranking list cannot be empty.")
        self.pairwise_matrix = self._create_pairwise_matrix()
        self.weights = self._calculate_priority_vector()
        self.consistency_ratio = self._check_consistency()

    def _create_pairwise_matrix(self) -> np.ndarray:
        n = self.num_criteria
        matrix = np.ones((n, n))
        rank_map = {crit_id: i for i, crit_id in enumerate(self.rankings)}
        
        # Menggunakan skala Saaty 1-9
        # Perbedaan peringkat 0 -> 1 (sama penting)
        # Perbedaan peringkat 1 -> 3
        # Perbedaan peringkat 2 -> 5
        # dst.
        for i in range(n):
            for j in range(i + 1, n):
                rank_i = list(rank_map.keys()).index(self.rankings[i])
                rank_j = list(rank_map.keys()).index(self.rankings[j])
                
                diff = abs(rank_i - rank_j)
                importance = min(1 + 2 * diff, 9) # Skala Saaty yang disederhanakan
                
                if rank_i < rank_j:
                    matrix[i, j] = importance
                    matrix[j, i] = 1 / importance
                else:
                    matrix[i, j] = 1 / importance
                    matrix[j, i] = importance
        return matrix

    def _calculate_priority_vector(self) -> Dict[int, float]:
        if self.num_criteria == 1:
            return {self.rankings[0]: 1.0}
            
        eigenvalues, eigenvectors = np.linalg.eig(self.pairwise_matrix)
        max_eigenvalue_index = np.argmax(eigenvalues)
        priority_vector = np.real(eigenvectors[:, max_eigenvalue_index])
        normalized_vector = priority_vector / np.sum(priority_vector)
        
        weights_dict = {self.rankings[i]: normalized_vector[i] for i in range(self.num_criteria)}
        return weights_dict

    def _check_consistency(self) -> float:
        if self.num_criteria <= 2:
            return 0.0

        RI_TABLE = {
            1: 0.0, 2: 0.0, 3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35,
            8: 1.40, 9: 1.45, 10: 1.49, 11: 1.51, 12: 1.54, 13: 1.56, 14: 1.57, 15: 1.58
        }
        
        lambda_max = np.max(np.real(np.linalg.eigvals(self.pairwise_matrix)))
        ci = (lambda_max - self.num_criteria) / (self.num_criteria - 1)
        ri = RI_TABLE.get(self.num_criteria, 1.58)
        
        if ri == 0:
            return 0.0
        
        return ci / ri