import pandas as pd
import numpy as np
from typing import Dict, Any
from core.scoring import calculate_quality_scores

def build_dataset_context(df: pd.DataFrame, dataset_name: str, reports: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a comprehensive, serializable dictionary of dataset statistics, schema, 
    quality rankings, and target variables for injection into the AI prompt.
    """
    if df is None or df.empty:
        return {}
        
    # Extract columns
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Missing values
    missing_by_col = df.isnull().sum().to_dict()
    total_nulls = int(df.isnull().sum().sum())
    null_percent = (total_nulls / (len(df) * len(df.columns))) * 100 if len(df) > 0 and len(df.columns) > 0 else 0.0
    
    # Duplicates
    dup_rows = int(df.duplicated().sum())
    
    # Unique values
    uniques = {col: int(df[col].nunique()) for col in df.columns}
    
    # Outliers
    outliers_stat = reports.get("OutliersDetector", {}).get("statistics", {}).get("outliers_by_column", {})
    total_outliers = reports.get("OutliersDetector", {}).get("statistics", {}).get("total_outliers", 0)
    
    # High Correlations (> 0.5)
    high_correlations = []
    if len(num_cols) >= 2:
        try:
            corr_matrix = df[num_cols].corr()
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    val = corr_matrix.iloc[i, j]
                    if abs(val) > 0.5 and not pd.isna(val):
                        high_correlations.append(f"{num_cols[i]} & {num_cols[j]} ({val:.2f})")
        except Exception:
            pass
            
    # Target Column Auto-detection
    target_keywords = ["target", "label", "class", "churn", "status", "outcome", "y", "clicked", "purchased"]
    target_col = None
    for col in df.columns:
        if col.lower() in target_keywords:
            target_col = col
            break
    if not target_col and cat_cols:
        # Default to low cardinality categorical column
        target_col = min(cat_cols, key=lambda c: df[c].nunique())
    if not target_col:
        target_col = df.columns[-1]
        
    health_score, ml_readiness = calculate_quality_scores(df, reports)

    # Best features (high completeness, high uniqueness)
    best_features = []
    for col in df.columns:
        null_pct = (df[col].isnull().sum() / len(df)) * 100 if len(df) > 0 else 100
        if null_pct < 5 and df[col].nunique() > 1:
            best_features.append(col)
            
    # Risk warnings
    risk_warnings = []
    if null_percent > 10:
        risk_warnings.append("High missingness density (>10%) can skew estimator weights.")
    if dup_rows > 0:
        risk_warnings.append(f"Found {dup_rows} duplicate observations leading to over-fitted estimator runs.")
    if total_outliers > 0:
        risk_warnings.append(f"Detected {total_outliers} outlier cells that might distort linear parameters.")
        
    return {
        "dataset_name": dataset_name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "column_types": {col: str(df[col].dtype) for col in df.columns},
        "missing_values": missing_by_col,
        "total_missing": total_nulls,
        "missing_percentage": null_percent,
        "duplicate_rows": dup_rows,
        "unique_values": uniques,
        "categorical_columns": cat_cols,
        "numerical_columns": num_cols,
        "high_correlations": high_correlations,
        "target_column": target_col,
        "total_outliers": total_outliers,
        "health_score": health_score,
        "ml_readiness_score": ml_readiness,
        "best_features": best_features[:3],
        "risk_warnings": risk_warnings
    }
