import numpy as np
from scipy.stats import entropy
import warnings

warnings.filterwarnings('ignore')

def calculate_kl(expected, actual, bins=10):
    """Calculates KL Divergence between two distributions"""
    if len(expected) == 0 or len(actual) == 0:
        return 0.0
        
    min_val = min(np.min(expected), np.min(actual))
    max_val = max(np.max(expected), np.max(actual))
    
    if min_val == max_val:
        return 0.0
        
    expected_hist, _ = np.histogram(expected, bins=bins, range=(min_val, max_val))
    actual_hist, _ = np.histogram(actual, bins=bins, range=(min_val, max_val))
    
    expected_prob = expected_hist / np.sum(expected_hist)
    actual_prob = actual_hist / np.sum(actual_hist)
    
    # Avoid zero division
    expected_prob = np.where(expected_prob == 0, 1e-6, expected_prob)
    actual_prob = np.where(actual_prob == 0, 1e-6, actual_prob)
    
    return float(entropy(actual_prob, expected_prob))
