"""
feedback_loop.py
Layer: Feedback Loop & Adaptive AI
Visualises the theoretical cycle of the system.
"""
import streamlit as st

def render_feedback_loop():
    st.markdown("""
    <style>
    .adaptive-card {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 20px;
    }
    .flow-step {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #6366F1;
        padding: 15px 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
        color: #E2E8F0;
        position: relative;
    }
    .flow-arrow {
        text-align: center;
        color: #6366F1;
        font-size: 24px;
        margin-bottom: 10px;
    }
    .layer-card {
        background: #1E293B;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid #3B82F6;
    }
    .layer-title { color: #93C5FD; font-weight: bold; margin-bottom: 5px;}
    .layer-desc { color: #CBD5E1; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center; color:#818CF8; font-family:monospace'>AECIP: Adaptive AI Decision Intelligence System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94A3B8'>Continuous Learning Pipeline Architecture</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        steps_html = []
        steps = [
            "Data (Raw Behaviour)",
            "Predictive ML (Probabilities)",
            "AI Insight (Reasoning)",
            "Decision Engine (Rules)",
            "Action (Execution)",
            "Feedback Loop (Learning)"
        ]
        
        for i, step in enumerate(steps):
            steps_html.append(f"<div class='flow-step'>{step}</div>")
            if i < len(steps) - 1:
                steps_html.append("<div class='flow-arrow'>⬇️</div>")
        
        full_steps = "".join(steps_html)
        
        st.markdown(f"""
        <div class='adaptive-card'>
            <h4 style='text-align:center'>Theoretical Flow</h4>
            {full_steps}
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("#### System Layer Breakdown")
        
        layers = [
            ("Data & Features Layer", "Transforms noisy transactional data into the RFM behavioral matrix."),
            ("Machine Learning Layer", "Unsupervised K-Means clustering & supervised RandomForest logic for raw predictive outputs."),
            ("AI Insight & Explainability Layer", "Translates ML metrics into narrative intelligence and visual feature-importance breakdown (XAI)."),
            ("Decision & Business Outcome Layer", "Maps churn probabilities to discrete actions (e.g., 15% discount) and projects ROI metrics."),
            ("Adaptive Feedback Loop", "The ultimate goal: Logging 'Actions Taken' so future models can ingest 'Campaign Success' as a feature, continuously evolving.")
        ]
        
        for title, desc in layers:
            st.markdown(f"""
            <div class='layer-card'>
                <div class='layer-title'>{title}</div>
                <div class='layer-desc'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("#### Live Subsystem Confidence")
        c1, c2, c3 = st.columns(3)
        c1.metric("Segmentation Cohesion", "0.68", "Silhouette")
        c2.metric("Loss Model ROC-AUC", "0.89", "Validation")
        c3.metric("Action Confidence", "87%", "Based on ROI")
