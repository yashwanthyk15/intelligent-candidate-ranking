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
    
    # Plotly Radar Chart
    df_radar = pd.DataFrame(dict(r=values, theta=categories))
    fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0, 1])
    fig.update_traces(fill='toself')
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        title=f"Candidate: {result_dict['candidate_id']}",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

custom_css = """
body {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.gradio-container {
    box-shadow: 0 20px 40px rgba(0,0,0,0.2) !important;
    border-radius: 20px !important;
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    padding: 25px !important;
}
button {
    box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
    transition: all 0.3s ease 0s !important;
    border-radius: 12px !important;
}
button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 20px rgba(0,0,0,0.2) !important;
}
"""

with gr.Blocks(title="Redrob Hackathon - Sandbox", theme=gr.themes.Soft(), css=custom_css) as app:
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
                title_plot = gr.BarPlot(x="Title", y="Count", title="Title Distribution (Top 100)", vertical=False, tooltip=["Title", "Count"])

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
    app.launch()
