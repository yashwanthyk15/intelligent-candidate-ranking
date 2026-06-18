import gradio as gr
import pandas as pd
import time
from pathlib import Path

# Import our backend ranking logic
from rank import process_candidates, generate_output

def run_ranking(file_obj):
    if file_obj is None:
        return None, "Please upload a candidates.jsonl file.", None
    
    start_time = time.time()
    input_path = file_obj.name
    
    # Run our exact hackathon logic
    results = process_candidates(input_path)
    
    # Write to CSV
    out_path = "sandbox_submission.csv"
    generate_output(results, out_path)
    
    # Load for UI display
    df = pd.read_csv(out_path)
    
    elapsed = time.time() - start_time
    total_processed = len(results['all_scored']) + len(results['honeypots'])
    status = f"✅ Successfully processed {total_processed} candidates in {elapsed:.2f} seconds."
    
    return df, status, out_path

with gr.Blocks(title="Redrob Hackathon - Sandbox", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏆 Intelligent Candidate Ranking — Sandbox Demo")
    gr.Markdown("""
    **Architecture:** 6-Dimension Feature Scoring + Anti-Gaming Penalty Engine
    **Constraints:** CPU only, ≤ 16GB RAM, No external APIs, < 300s runtime.
    
    Upload a `candidates.jsonl` file (up to 100K records) to run the full pipeline.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload candidates.jsonl", file_types=[".jsonl"])
            run_btn = gr.Button("🚀 Run Ranking Pipeline", variant="primary")
            status_out = gr.Markdown("**Status:** Waiting for upload...")
            download_out = gr.File(label="Download sandbox_submission.csv")
            
        with gr.Column(scale=2):
            table_out = gr.Dataframe(label="Top 100 Ranked Candidates", wrap=True)
            
    run_btn.click(
        fn=run_ranking,
        inputs=[file_input],
        outputs=[table_out, status_out, download_out]
    )

if __name__ == "__main__":
    app.launch()
