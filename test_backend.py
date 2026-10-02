import pandas as pd
import numpy as np
from core.pipeline import PipelineManager
from core.cleaners import (
    MeanImputationCleaner,
    MedianImputationCleaner,
    ModeImputationCleaner,
    KNNImputationCleaner,
    DuplicateRemovalCleaner,
    IQROutlierCleaner,
    ZScoreOutlierCleaner,
    IsolationForestCleaner,
    ColumnRenamingCleaner,
    TextNormalizationCleaner,
    LabelStandardizationCleaner,
    FeatureScalingCleaner,
    L2NormalizationCleaner,
    FeatureEncodingCleaner
)

def run_tests():
    print("=== Generating Dirty Mock Data ===")
    data = {
        "col_numeric": [1.0, 2.0, np.nan, 4.0, 100.0, 2.0], # Nulls, outliers (100)
        "col_text": [" Yes", "No ", "Yes", "Maybe", np.nan, "Yes"], # Duplicate, trailing space, null
        "col_const": [10, 10, 10, 10, 10, 10], # Constant
        "col_empty": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], # Empty
        "col_date": ["2024-01-01", "2024-01-02", "invalid-date", "2024-01-04", "2024-01-05", "2024-01-02"]
    }
    df = pd.DataFrame(data)
    # Append duplicate row
    df = pd.concat([df, df.iloc[[1]]], ignore_index=True)
    print(df)
    print()

    print("=== Running 10-Anomaly Detectors Suite ===")
    manager = PipelineManager()
    reports = manager.run_all_detections(df)
    
    for name, r in reports.items():
        print(f"[{name}]")
        print(f"  Confidence Score: {r['confidence_score']}")
        print(f"  Problem Found: {r['problem']}")
        print(f"  Solution Suggested: {r['solution']}")
        print(f"  Stats: {r['statistics']}")
        print()

    print("=== Executing 14-Repair Cleaners Suite ===")
    
    # 1. Column Renaming
    df, meta = ColumnRenamingCleaner({"col_numeric": "target_feature"}).clean(df)
    print(f"Rename logs: {meta['logs']}")
    
    # 2. Duplicate Removal
    df, meta = DuplicateRemovalCleaner().clean(df)
    print(f"Duplicate logs: {meta['logs']}")
    
    # 3. Median Imputation
    df, meta = MedianImputationCleaner(["target_feature"]).clean(df)
    print(f"Median logs: {meta['logs']}")
    
    # 4. Mode Imputation
    df, meta = ModeImputationCleaner(["col_text"]).clean(df)
    print(f"Mode logs: {meta['logs']}")
    
    # 5. Text Normalization (casing and spaces)
    df, meta = TextNormalizationCleaner(["col_text"]).clean(df)
    print(f"Text Normalization logs: {meta['logs']}")
    
    # 6. IQR Outlier Clipping
    df, meta = IQROutlierCleaner(["target_feature"], multiplier=1.5).clean(df)
    print(f"IQR Outlier logs: {meta['logs']}")
    
    # 7. Z-Score Outlier Drop
    df, meta = ZScoreOutlierCleaner(["target_feature"], threshold=2.0).clean(df)
    print(f"Z-Score logs: {meta['logs']}")
    
    # 8. KNN Imputer
    df, meta = KNNImputationCleaner(["target_feature"]).clean(df)
    print(f"KNN logs: {meta['logs']}")
    
    # 9. Isolation Forest
    df, meta = IsolationForestCleaner(["target_feature"], contamination=0.1).clean(df)
    print(f"Isolation Forest logs: {meta['logs']}")
    
    # 10. Label Standardization
    df, meta = LabelStandardizationCleaner({"col_text": {"yes": "confirmed"}}).clean(df)
    print(f"Label Standardization logs: {meta['logs']}")
    
    # 11. Scaling (Standard)
    # Drop empty and dates for scaling/norm testing
    df_scal = df.drop(columns=["col_empty", "col_date", "col_text"])
    df_scal, meta = FeatureScalingCleaner(method="standard").clean(df_scal)
    print(f"Scaling logs: {meta['logs']}")
    
    # 12. Normalization (L2)
    df_norm, meta = L2NormalizationCleaner().clean(df_scal)
    print(f"L2 logs: {meta['logs']}")
    
    # 13. Encoding (One-hot)
    df_enc, meta = FeatureEncodingCleaner(["col_text"]).clean(df.drop(columns=["col_empty", "col_date"]))
    print(f"Encoding logs: {meta['logs']}")
    
    print("\n=== All Tests Completed Successfully ===")

if __name__ == "__main__":
    run_tests()
