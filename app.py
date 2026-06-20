import gradio as gr
import pandas as pd
import time
import plotly.express as px
from pathlib import Path

# Import our backend ranking logic
from rank import process_candidates, generate_output

def run_ranking(file_obj):
    if file_obj is None:
        return None, "Please upload a candidates.jsonl file.", None, None, None, None
    
    start_time = time.time()
    input_path = file_obj.name
    
    # Run our exact hackathon logic
    results, stats = process_candidates(input_path)
    
    # Write to CSV
    out_path = "sandbox_submission.csv"
    generate_output(results, out_path)
    
    # Load for UI display
    df = pd.read_csv(out_path)
    
    elapsed = time.time() - start_time
    status = f"✅ Successfully processed {stats['total_processed']:,} candidates in {elapsed:.2f} seconds."
    
    # Insights Data 1: Honeypots vs Valid
    hp_df = pd.DataFrame({
        "Category": ["Valid Candidates", "Honeypots Detected"],
        "Count": [stats['total_processed'] - stats['honeypots'], stats['honeypots']]
    })
    
    # Insights Data 2: Top 100 Titles Distribution
    titles = [res[2]['candidate']['profile'].get('current_title', 'Unknown') for res in results[:100]]
    title_counts = pd.Series(titles).value_counts().reset_index()
    title_counts.columns = ["Title", "Count"]
    
    return df, status, out_path, results, hp_df, title_counts

def show_radar_chart(evt: gr.SelectData, results_state):
    if not results_state:
        return None
        
    row_idx = evt.index[0]
    if row_idx >= len(results_state):
        return None
        
    # Get candidate info
    _, _, result_dict = results_state[row_idx]
    dim_scores = result_dict.get('dim_scores', {})
    
    # Extract dimensions
    categories = ['Role Alignment', 'Shipped Systems', 'Tech Depth', 'Experience', 'Behavioral', 'Location', 'BM25 Semantic']
    keys = ['role_alignment', 'shipped_systems', 'tech_depth', 'experience', 'behavioral', 'location', 'bm25_semantic']
    values = [dim_scores.get(k, 0.0) for k in keys]
    
    # Plotly Radar Chart (Dark Mode)
    df_radar = pd.DataFrame(dict(r=values, theta=categories))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0, 1], template="plotly_dark")
    fig.update_traces(fill='toself', line_color='#8b5cf6', fillcolor='rgba(139, 92, 246, 0.3)')
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], color='#52525b', gridcolor='#27272a'),
            angularaxis=dict(color='#e4e4e7', gridcolor='#27272a')
        ),
        showlegend=False,
        title=dict(text=f"Candidate: {result_dict['candidate_id']}", font=dict(color='#fafafa')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

custom_css = """
body, .gradio-container {
    background-color: #09090b !important;
    color: #fafafa !important;
}
.gradio-container {
    border: 1px solid #27272a !important;
    box-shadow: 0 0 40px rgba(0,0,0,0.5) !important;
    border-radius: 12px !important;
}
button.primary {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.39) !important;
    transition: transform 0.2s ease !important;
}
button.primary:hover {
    transform: translateY(-2px) !important;
}
table {
    border-collapse: collapse !important;
    overflow: hidden !important;
    border-radius: 8px !important;
}
th {
    background-color: #18181b !important;
    color: #a1a1aa !important;
    border-bottom: 1px solid #27272a !important;
}
td {
    background-color: #09090b !important;
    border-bottom: 1px solid #27272a !important;
}
tr:hover td {
    background-color: #27272a !important;
}
"""

with gr.Blocks(title="Redrob Hackathon - Sandbox") as app:
    gr.Markdown("# 🏆 Intelligent Candidate Ranking — God-Level Sandbox")
    gr.Markdown("""
    **Architecture:** 6-Dimension Feature Scoring + Pure-Python BM25 Relevance Engine
    **Constraints:** CPU only, ≤ 16GB RAM, No external APIs, < 300s runtime.
    """)
    
    # Hidden state to store full candidate results for the radar chart
    results_state = gr.State()
    
    with gr.Tabs():
        with gr.TabItem("🚀 Ranking Engine"):
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(label="Upload candidates.jsonl", file_types=[".jsonl"])
                    run_btn = gr.Button("⚡ Run AI Ranking Pipeline", variant="primary")
                    status_out = gr.Markdown("**Status:** Waiting for upload...")
                    download_out = gr.File(label="Download sandbox_submission.csv")
                    
                    gr.Markdown("### 🔍 Explainable AI")
                    gr.Markdown("Select a candidate from the table to view their Radar Profile.")
                    radar_plot = gr.Plot(label="Candidate Dimension Breakdown")
                    
                with gr.Column(scale=2):
                    table_out = gr.Dataframe(label="Top 100 Ranked Candidates (Click a row to inspect)", interactive=False)
                    
        with gr.TabItem("📊 Dataset Forensics"):
            gr.Markdown("### Macro Analysis of Processed Candidates")
            with gr.Row():
                hp_plot = gr.BarPlot(x="Category", y="Count", title="Honeypots vs Valid (Total Dataset)", tooltip=["Category", "Count"])
                title_plot = gr.BarPlot(x="Count", y="Title", title="Title Distribution (Top 100)", tooltip=["Title", "Count"])

    run_btn.click(
        fn=run_ranking,
        inputs=[file_input],
        outputs=[table_out, status_out, download_out, results_state, hp_plot, title_plot]
    )
    
    # Trigger radar chart when a row is selected
    table_out.select(
        fn=show_radar_chart,
        inputs=[results_state],
        outputs=[radar_plot]
    )

if __name__ == "__main__":
    app.launch(theme=gr.themes.Base(), css=custom_css)
