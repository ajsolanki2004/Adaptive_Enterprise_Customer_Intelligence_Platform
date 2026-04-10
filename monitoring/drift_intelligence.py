from monitoring.psi_calculator import calculate_psi
from monitoring.kl_divergence import calculate_kl
from config.db_config import get_connection

class DriftIntelligence:
    @staticmethod
    def evaluate_drift(expected_data, actual_data):
        """Calculates composite drift score and logs it to PostgreSQL"""
        # 1. Population Stability Index (PSI): Heavy enterprise standard for data shifts
        psi_score = calculate_psi(expected_data, actual_data)
        
        # 2. Kullback-Leibler Divergence (KL): Statistical entropy standard for distributions
        kl_score = calculate_kl(expected_data, actual_data)
        
        # 3. Create a weighted custom composite score prioritizing PSI slightly
        composite_score = 0.6 * psi_score + 0.4 * kl_score
        
        # 4. Define our hardcoded risk thresholds
        if composite_score <= 0.1:
            severity = "Normal"
        elif composite_score <= 0.25:
            severity = "Moderate"
        else:
            severity = "Severe"
            
        print(f"Drift Evaluated - PSI: {psi_score:.4f}, KL: {kl_score:.4f}, Composite: {composite_score:.4f} ({severity})")
        
        # 5. Log this audit trait permanently into the Database
        DriftIntelligence.log_drift(psi_score, kl_score, composite_score, severity)
        
        return {
            'psi': psi_score,
            'kl': kl_score,
            'composite': composite_score,
            'severity': severity
        }
        
    @staticmethod
    def log_drift(psi, kl, composite, severity):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO drift_metrics (psi_score, kl_score, composite_score, severity_level)
                VALUES (%s, %s, %s, %s)
            """, (float(psi), float(kl), float(composite), str(severity)))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error logging drift metrics: {e}")
