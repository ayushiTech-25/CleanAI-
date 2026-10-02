import pandas as pd


def normalize_detector_report(report: object, detector_name: str) -> dict:
    """Return the stable detector contract consumed by every UI surface."""
    if not isinstance(report, dict):
        return {
            "problem": f"{detector_name} returned an invalid result.",
            "solution": "Review the detector implementation and input dataset.",
            "statistics": {},
            "explanation": "The detector response was not a dictionary.",
            "confidence_score": 0.0,
        }

    problem = report.get("problem")
    solution = report.get("solution")
    statistics = report.get("statistics")
    explanation = report.get("explanation")
    confidence = report.get("confidence_score", 0.0)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.0

    return {
        "problem": problem if isinstance(problem, str) or problem is None else str(problem),
        "solution": solution if isinstance(solution, str) or solution is None else str(solution),
        "statistics": statistics if isinstance(statistics, dict) else {},
        "explanation": explanation if isinstance(explanation, str) else "No detector explanation available.",
        "confidence_score": confidence,
    }
from core.detectors import (
    MissingValuesDetector,
    DuplicatesDetector,
    DataTypeDetector,
    OutliersDetector,
    ConstantColumnsDetector,
    EmptyColumnsDetector,
    HighCardinalityDetector,
    MixedTextDetector,
    ExtraSpacesDetector,
    InvalidDateDetector
)

class PipelineManager:
    """
    Coordinates data quality anomaly scanning.
    Aggregates results from all 10 base detectors.
    """
    
    def __init__(self):
        self.detectors = [
            MissingValuesDetector(),
            DuplicatesDetector(),
            DataTypeDetector(),
            OutliersDetector(),
            ConstantColumnsDetector(),
            EmptyColumnsDetector(),
            HighCardinalityDetector(),
            MixedTextDetector(),
            ExtraSpacesDetector(),
            InvalidDateDetector()
        ]
        
    def run_all_detections(self, df: pd.DataFrame) -> dict:
        """
        Executes all 10 anomaly detections on a DataFrame.
        
        Returns:
            dict: Mapping of Detector class name to its diagnosis report dictionary.
        """
        reports = {}
        if df is None or df.empty:
            return reports
            
        for detector in self.detectors:
            name = detector.__class__.__name__
            try:
                reports[name] = normalize_detector_report(detector.detect(df), name)
            except Exception as e:
                reports[name] = {
                    "problem": f"Scanning error: {str(e)}",
                    "solution": "Verify input dataframe layout.",
                    "statistics": {},
                    "explanation": "Critical error during detector execution.",
                    "confidence_score": 0.0
                }
        return reports

import streamlit as st

@st.cache_data
def cached_run_all_detections(df: pd.DataFrame) -> dict:
    """Cached wrapper around PipelineManager to speed up UI loads."""
    manager = PipelineManager()
    return manager.run_all_detections(df)
