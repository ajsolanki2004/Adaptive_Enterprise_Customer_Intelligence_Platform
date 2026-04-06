import numpy as np
import warnings

warnings.filterwarnings('ignore')

def calculate_psi(expected, actual, buckets=10):
    """Calculates the Population Stability Index"""
    def scale_range (input, min, max):
        # Prevent division by zero if input array is constant
        diff = np.max(input) - np.min(input)
        if diff == 0:
            diff = 1e-6
        input_scaled = (input - np.min(input)) / diff
        input_scaled = input_scaled * (max - min) + min
        return input_scaled

    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    breakpoints = np.arange(0, buckets + 1) / buckets * 100
    breakpoints = scale_range(breakpoints, np.min(expected), np.max(expected))
    
    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
    
    # Avoid zero division
    expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
    actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
    
    psi_value = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
    return float(psi_value)
