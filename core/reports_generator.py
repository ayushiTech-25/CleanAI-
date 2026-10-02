import os
import re
from datetime import datetime
import pandas as pd
from fpdf import FPDF

class CleanAIPDF(FPDF):
    """Custom FPDF subclass to establish corporate headers, footers, and page numbers."""
    
    def header(self):
        # Draw top accent bar
        self.set_fill_color(99, 102, 241) # Indigo (6366f1)
        self.rect(0, 0, 210, 4, "F")
        
        # Add company title
        self.set_xy(10, 10)
        self.set_font("helvetica", "B", 14)
        self.set_text_color(24, 24, 27) # Zinc 900
        self.cell(0, 10, "CleanAI | Data Quality & Readiness Audit", ln=1, align="L")
        
        # Draw horizontal separating line
        self.set_draw_color(228, 228, 231) # Zinc 200
        self.line(10, 22, 200, 22)
        self.ln(12)
        
    def footer(self):
        # Draw bottom horizontal separator line
        self.set_draw_color(228, 228, 231)
        self.line(10, 280, 200, 280)
        
        # Set cursor for footer text
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(113, 113, 122) # Zinc 500
        
        # Render page number and watermark
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  CleanAI Production Report", align="C")

class PDFReportGenerator:
    """Compiles tabular profile metrics, alerts, cleaner steps, and AI feedback into a PDF document."""
    
    @staticmethod
    def clean_text_for_pdf(text: str) -> str:
        """Removes emojis and standardizes quotes/symbols to prevent FPDF cell encode failures."""
        if not text:
            return ""
        # Strip common emoji ranges and arrows
        text = re.sub(r"[^\x00-\x7F]+", "", text)
        text = text.replace("➔", "->").replace("↑", "+").replace("↓", "-").replace("`", "'")
        return text

    def generate_report(self, 
                        df: pd.DataFrame, 
                        orig_df: pd.DataFrame, 
                        reports: dict, 
                        history: list, 
                        ai_summary: str, 
                        ai_readiness: str, 
                        filename: str) -> str:
        """
        Builds a styled business PDF document.
        
        Returns:
            str: Path to the generated PDF document.
        """
        # Calculate key numbers
        total_rows = len(df)
        total_cols = len(df.columns)
        null_cells = df.isnull().sum().sum()
        total_cells = total_rows * total_cols
        null_pct = (null_cells / total_cells) * 100 if total_cells > 0 else 0.0
        dupes = df.duplicated().sum()
        
        # Calculate dynamic health scores matching dashboard page
        outlier_cols = len(reports.get("OutliersDetector", {}).get("statistics", {}).get("outliers_by_column", {}))
        wrong_types = len(reports.get("DataTypeDetector", {}).get("statistics", {}).get("columns_to_cast", {}))
        const_cols = len(reports.get("ConstantColumnsDetector", {}).get("statistics", {}).get("constant_columns", {}))
        empty_cols = len(reports.get("EmptyColumnsDetector", {}).get("statistics", {}).get("empty_columns", []))
        card_cols = len(reports.get("HighCardinalityDetector", {}).get("statistics", {}).get("high_cardinality_columns", {}))
        space_cols = len(reports.get("ExtraSpacesDetector", {}).get("statistics", {}).get("space_anomalies", {}))
        date_cols = len(reports.get("InvalidDateDetector", {}).get("statistics", {}).get("invalid_date_columns", {}))
        
        health_score = 100.0 - (null_pct * 1.2 + (dupes / total_rows * 100 if total_rows > 0 else 0) + outlier_cols * 4.0 + wrong_types * 5.0 + const_cols * 10.0 + empty_cols * 15.0 + card_cols * 4.0 + space_cols * 2.0 + date_cols * 8.0)
        health_score = max(0, min(100, int(health_score)))
        
        ml_readiness = 100.0 - (null_pct * 2.2 + (dupes / total_rows * 100 if total_rows > 0 else 0)*0.5 + outlier_cols * 8.0 + wrong_types * 6.0 + const_cols * 12.0 + empty_cols * 20.0 + card_cols * 5.0 + space_cols * 1.0 + date_cols * 10.0)
        ml_readiness = max(0, min(100, int(ml_readiness)))

        # Initialize FPDF
        pdf = CleanAIPDF(orientation="P", unit="mm", format="A4")
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # --- TITLE & TIMESTAMP ---
        pdf.set_y(26)
        pdf.set_font("helvetica", "B", 18)
        pdf.set_text_color(24, 24, 27) # Zinc 900
        pdf.cell(0, 10, "DATA READINESS SUMMARY REPORT", ln=1, align="L")
        
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(113, 113, 122) # Zinc 500
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 5, f"Report generated on: {timestamp_str}  |  Identifier: CAI-{datetime.now().strftime('%Y%m%d%H%M')}", ln=1, align="L")
        pdf.ln(5)
        
        # --- STATS CARDS GRID ---
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(63, 63, 70) # Zinc 700
        pdf.cell(0, 8, "1. Executive Overview Metrics", ln=1, align="L")
        pdf.ln(2)
        
        # Draw metric card grid blocks
        # First row cards
        card_w = 45
        card_h = 16
        
        # Card 1: Total Observations
        x_start = 10
        pdf.set_xy(x_start, pdf.get_y())
        pdf.set_draw_color(228, 228, 231)
        pdf.set_fill_color(250, 250, 250)
        pdf.rect(x_start, pdf.get_y(), card_w, card_h, "FD")
        pdf.set_xy(x_start + 3, pdf.get_y() + 2)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(113, 113, 122)
        pdf.cell(card_w - 6, 4, "OBSERVATIONS", ln=1)
        pdf.set_xy(x_start + 3, pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(24, 24, 27)
        pdf.cell(card_w - 6, 5, f"{total_rows:,}")
        
        # Card 2: Features
        pdf.set_xy(x_start + card_w + 5, pdf.get_y() - 8)
        pdf.rect(x_start + card_w + 5, pdf.get_y(), card_w, card_h, "FD")
        pdf.set_xy(x_start + card_w + 8, pdf.get_y() + 2)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(113, 113, 122)
        pdf.cell(card_w - 6, 4, "TOTAL FEATURES", ln=1)
        pdf.set_xy(x_start + card_w + 8, pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(24, 24, 27)
        pdf.cell(card_w - 6, 5, f"{total_cols}")
        
        # Card 3: Health Score
        pdf.set_xy(x_start + (card_w * 2) + 10, pdf.get_y() - 8)
        pdf.rect(x_start + (card_w * 2) + 10, pdf.get_y(), card_w, card_h, "FD")
        pdf.set_xy(x_start + (card_w * 2) + 13, pdf.get_y() + 2)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(113, 113, 122)
        pdf.cell(card_w - 6, 4, "HEALTH INDEX", ln=1)
        pdf.set_xy(x_start + (card_w * 2) + 13, pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(16, 185, 129) # Emerald Green (10b981)
        pdf.cell(card_w - 6, 5, f"{health_score}%")
        
        # Card 4: ML Readiness
        pdf.set_xy(x_start + (card_w * 3) + 15, pdf.get_y() - 8)
        pdf.rect(x_start + (card_w * 3) + 15, pdf.get_y(), card_w, card_h, "FD")
        pdf.set_xy(x_start + (card_w * 3) + 18, pdf.get_y() + 2)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(113, 113, 122)
        pdf.cell(card_w - 6, 4, "ML READINESS", ln=1)
        pdf.set_xy(x_start + (card_w * 3) + 18, pdf.get_y() + 2)
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(99, 102, 241) # Indigo (6366f1)
        pdf.cell(card_w - 6, 5, f"{ml_readiness}%")
        
        pdf.set_xy(10, pdf.get_y() + 10)
        pdf.ln(5)
        
        # --- QUALITY ANOMALY TABLE ---
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(63, 63, 70)
        pdf.cell(0, 8, "2. Active Quality Anomaly Alerts", ln=1, align="L")
        pdf.ln(2)
        
        # Table Headers
        pdf.set_font("helvetica", "B", 9)
        pdf.set_fill_color(244, 244, 245) # Zinc 100
        pdf.set_text_color(39, 39, 42)
        pdf.cell(45, 8, "Anomaly Scanner", border=1, ln=0, fill=True)
        pdf.cell(105, 8, "Problem Diagnosis", border=1, ln=0, fill=True)
        pdf.cell(40, 8, "Resolution Priority", border=1, ln=1, fill=True)
        
        # Table Contents
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(63, 63, 70)
        
        has_alerts = False
        for det_name, report in reports.items():
            if report.get("problem"):
                has_alerts = True
                clean_name = det_name.replace("Detector", "")
                prob_text = self.clean_text_for_pdf(report["problem"])
                sol_text = self.clean_text_for_pdf(report["solution"])
                
                # Check priority based on names
                priority = "High" if "Missing" in det_name or "Empty" in det_name or "Invalid" in det_name else "Medium"
                
                pdf.cell(45, 10, f" {clean_name}", border=1)
                
                # Render multi-line cell text cleanly
                x = pdf.get_x()
                y = pdf.get_y()
                pdf.multi_cell(105, 5, f" {prob_text}\n Fix: {sol_text}", border=1)
                pdf.set_xy(x + 105, y)
                pdf.cell(40, 10, f" {priority}", border=1, ln=1)
                
        if not has_alerts:
            pdf.cell(190, 8, " No quality anomalies detected. All quality thresholds satisfied.", border=1, ln=1)
            
        pdf.ln(8)
        
        # --- PIPELINE LOGS TABLE ---
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(63, 63, 70)
        pdf.cell(0, 8, "3. Repair Pipeline Execution Log", ln=1, align="L")
        pdf.ln(2)
        
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(35, 8, "Timestamp", border=1, ln=0, fill=True)
        pdf.cell(115, 8, "Cleaning Step Applied", border=1, ln=0, fill=True)
        pdf.cell(40, 8, "Result Status", border=1, ln=1, fill=True)
        
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(63, 63, 70)
        
        if history:
            for item in history:
                t_str = self.clean_text_for_pdf(item.get("timestamp", ""))
                a_str = self.clean_text_for_pdf(item.get("action", ""))
                aff_str = self.clean_text_for_pdf(item.get("affected", ""))
                
                pdf.cell(35, 8, f" {t_str}", border=1)
                pdf.cell(115, 8, f" {a_str} ({aff_str})", border=1)
                pdf.cell(40, 8, " Success (Applied)", border=1, ln=1)
        else:
            pdf.cell(190, 8, " No cleaning pipelines executed. Dataset remains in original state.", border=1, ln=1)
            
        pdf.ln(8)
        
        # --- AI DATA SCIENCE MEMO ---
        # Add new page if vertical cursor is too low
        if pdf.get_y() > 190:
            pdf.add_page()
            
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(63, 63, 70)
        pdf.cell(0, 8, "4. AI Data Scientist Audit Summary", ln=1, align="L")
        pdf.ln(2)
        
        # Clean markdown characters for PDF display
        clean_summary = self.clean_text_for_pdf(ai_summary)
        clean_readiness = self.clean_text_for_pdf(ai_readiness)
        
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(24, 24, 27)
        pdf.cell(0, 5, "Dataset Executive Memo:", ln=1)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(63, 63, 70)
        pdf.multi_cell(0, 4.5, clean_summary)
        pdf.ln(4)
        
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(24, 24, 27)
        pdf.cell(0, 5, "ML Estimator Readiness Rationale:", ln=1)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(63, 63, 70)
        pdf.multi_cell(0, 4.5, clean_readiness)
        
        # Output document to destination file path
        try:
            pdf.output(filename)
            return filename
        except Exception as e:
            raise RuntimeError(f"Error saving PDF report to file: {str(e)}")
