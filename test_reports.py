import os
import pandas as pd
from datetime import datetime
from core.pipeline import PipelineManager
from core.reports_generator import PDFReportGenerator

def test_exporters():
    print("=== Creating Mock Dataset ===")
    df = pd.DataFrame({
        "customer_id": ["USR-101", "USR-102", "USR-103", "USR-104"],
        "age": [25.0, 34.0, None, 45.0],
        "monthly_charges": [29.99, -15.0, 89.99, 120.0],
        "churn": ["Yes", "No", "yes", "No"]
    })
    orig_df = df.copy()
    
    # Run detectors
    manager = PipelineManager()
    reports = manager.run_all_detections(df)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Target directories
    os.makedirs("exports", exist_ok=True)
    
    print("\n=== Testing Multi-Format Exports ===")
    
    # 1. CSV Export
    csv_file = f"exports/cleanai_data_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved CSV: {csv_file}")
    assert os.path.exists(csv_file), "CSV generation failed"
    
    # 2. Excel Export
    excel_file = f"exports/cleanai_data_{timestamp}.xlsx"
    df.to_excel(excel_file, index=False, engine="openpyxl")
    print(f"Saved Excel: {excel_file}")
    assert os.path.exists(excel_file), "Excel generation failed"
    
    # 3. JSON Export
    json_file = f"exports/cleanai_data_{timestamp}.json"
    df.to_json(json_file, orient="records", indent=2)
    print(f"Saved JSON: {json_file}")
    assert os.path.exists(json_file), "JSON generation failed"
    
    # 4. Cleaning Log Export
    mock_history = [
        {"timestamp": "12:00:00", "action": "Initialized Dataset", "affected": "All Columns"},
        {"timestamp": "12:05:00", "action": "Dropped Duplicates", "affected": "Observations"}
    ]
    log_file = f"exports/cleanai_log_{timestamp}.json"
    import json
    with open(log_file, "w") as f:
        json.dump(mock_history, f, indent=2)
    print(f"Saved Cleaning Log: {log_file}")
    assert os.path.exists(log_file), "Cleaning Log generation failed"
    
    # 5. PDF Report Export
    pdf_file = f"exports/cleanai_report_{timestamp}.pdf"
    ai_summary = "### Executive Memo\nThe dataset exhibits completeness index. Column anomalies require mediation."
    ai_readiness = "### Readiness Rationale\nThe training viability index is 75%. Missing values require median imputation."
    
    gen = PDFReportGenerator()
    gen.generate_report(df, orig_df, reports, mock_history, ai_summary, ai_readiness, pdf_file)
    print(f"Saved PDF Report: {pdf_file}")
    assert os.path.exists(pdf_file), "PDF generation failed"
    
    print("\n=== All Reports and Data Formats Export Tests Passed ===")

if __name__ == "__main__":
    test_exporters()
