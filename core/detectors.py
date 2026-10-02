import pandas as pd
import numpy as np
from core.base import BaseDetector

class MissingValuesDetector(BaseDetector):
    """Detects missing/null cells in the dataset."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        total_cells = df.size
        null_counts = df.isnull().sum()
        total_nulls = null_counts.sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        
        problem = None
        solution = None
        if total_nulls > 0:
            problem = f"Found {total_nulls} missing cell(s) across {len(null_cols)} columns."
            solution = "Impute missing numeric values (mean/median/KNN) or categorical fields (mode/constant), or drop missing rows."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "total_null_count": int(total_nulls),
                "null_percentage": float(total_nulls / total_cells * 100) if total_cells > 0 else 0.0,
                "null_by_column": {k: int(v) for k, v in null_cols.items()}
            },
            "explanation": "Missing cells reduce dataset size and throw errors in training estimators. Imputations are necessary for ML readiness.",
            "confidence_score": 1.0
        }

class DuplicatesDetector(BaseDetector):
    """Detects duplicate rows in the dataset."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        dup_count = int(df.duplicated().sum())
        total_rows = len(df)
        
        problem = None
        solution = None
        if dup_count > 0:
            problem = f"Found {dup_count} duplicate row(s)."
            solution = "Apply duplicate row removal to keep unique observations."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "duplicate_count": dup_count,
                "duplicate_percentage": float(dup_count / total_rows * 100) if total_rows > 0 else 0.0
            },
            "explanation": "Identical rows bias machine learning estimators by overrepresenting redundant samples.",
            "confidence_score": 1.0
        }

class DataTypeDetector(BaseDetector):
    """Detects wrong, mixed, or sub-optimal data types in columns."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        columns_to_cast = {}
        
        for col in df.columns:
            if df[col].dtype == "object":
                non_nulls = df[col].dropna()
                if len(non_nulls) == 0:
                    continue
                
                # Check if it could be numeric
                numeric_parsed = pd.to_numeric(non_nulls, errors="coerce")
                valid_num_pct = numeric_parsed.notnull().sum() / len(non_nulls)
                if valid_num_pct >= 0.85:
                    columns_to_cast[col] = {
                        "suggested_type": "numeric",
                        "match_rate": float(valid_num_pct)
                    }
                    continue
                
                # Check if it could be datetime
                try:
                    date_parsed = pd.to_datetime(non_nulls, errors="coerce", format="mixed")
                    valid_date_pct = date_parsed.notnull().sum() / len(non_nulls)
                    if valid_date_pct >= 0.85:
                        columns_to_cast[col] = {
                            "suggested_type": "datetime",
                            "match_rate": float(valid_date_pct)
                        }
                except Exception:
                    pass
                    
        problem = None
        solution = None
        if len(columns_to_cast) > 0:
            cols_desc = ", ".join([f"'{c}' as {v['suggested_type']}" for c, v in columns_to_cast.items()])
            problem = f"Columns loaded with suboptimal datatypes: {cols_desc}."
            solution = "Cast object columns to their matching numeric or datetime signatures."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "columns_to_cast": columns_to_cast
            },
            "explanation": "Pandas frequently parses columns loaded with mixed structures or placeholders as object strings, disabling analytical operations.",
            "confidence_score": 0.95
        }

class OutliersDetector(BaseDetector):
    """Detects statistical outliers in numerical columns using IQR bounds (1.5 IQR)."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        num_cols = df.select_dtypes(include=["number"]).columns
        outliers_by_col = {}
        total_outliers = 0
        
        for col in num_cols:
            col_data = df[col].dropna()
            if len(col_data) < 5:
                continue
            
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
                
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
            count = int(outlier_mask.sum())
            if count > 0:
                outliers_by_col[col] = {
                    "count": count,
                    "percentage": float(count / len(col_data) * 100),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound)
                }
                total_outliers += count
                
        problem = None
        solution = None
        if total_outliers > 0:
            problem = f"Found {total_outliers} numerical outlier values across {len(outliers_by_col)} features."
            solution = "Clip outlier values using IQR bounds, scale inputs, or drop extreme values."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "total_outliers": total_outliers,
                "outliers_by_column": outliers_by_col
            },
            "explanation": "Outliers bias model estimations (especially linear / distance-based models) and skews statistical scaling.",
            "confidence_score": 0.85
        }

class ConstantColumnsDetector(BaseDetector):
    """Detects single-value columns (zero variance) which hold no predictive weight."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        constant_cols = {}
        for col in df.columns:
            unique_count = df[col].nunique(dropna=True)
            if unique_count == 1:
                constant_cols[col] = str(df[col].dropna().iloc[0])
                
        problem = None
        solution = None
        if len(constant_cols) > 0:
            problem = f"Found {len(constant_cols)} constant columns: {list(constant_cols.keys())}."
            solution = "Drop constant columns since they carry zero statistical information for ML models."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "constant_columns": constant_cols
            },
            "explanation": "Columns containing only one unique value are mathematically uninformative and cause division-by-zero scaling errors.",
            "confidence_score": 1.0
        }

class EmptyColumnsDetector(BaseDetector):
    """Detects empty columns (100% null cells)."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        empty_cols = []
        for col in df.columns:
            if df[col].isnull().all():
                empty_cols.append(col)
                
        problem = None
        solution = None
        if len(empty_cols) > 0:
            problem = f"Found {len(empty_cols)} completely empty columns: {empty_cols}."
            solution = "Drop empty columns from the training input array."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "empty_columns": empty_cols
            },
            "explanation": "Columns lacking any observational readings cannot be imputed or engineered, requiring deletion.",
            "confidence_score": 1.0
        }

class HighCardinalityDetector(BaseDetector):
    """Detects categorical columns containing excessive unique categories."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        high_card = {}
        
        for col in cat_cols:
            # Skip potential ID columns by verifying pattern or simple check
            if col.lower() in ["id", "customer_id", "user_id", "uuid"]:
                continue
                
            unique_count = df[col].nunique(dropna=True)
            total_rows = len(df)
            
            # Category threshold: >50 unique values or unique ratio > 35%
            if unique_count > 50 or (total_rows > 0 and (unique_count / total_rows) > 0.35):
                high_card[col] = {
                    "unique_values": unique_count,
                    "ratio": float(unique_count / total_rows) if total_rows > 0 else 0.0
                }
                
        problem = None
        solution = None
        if len(high_card) > 0:
            cols_desc = ", ".join([f"'{c}' ({v['unique_values']} classes)" for c, v in high_card.items()])
            problem = f"High cardinality detected in columns: {cols_desc}."
            solution = "Apply Target/Frequency Encoding, drop IDs, or bundle minority labels into an 'other' category."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "high_cardinality_columns": high_card
            },
            "explanation": "High cardinality columns cause one-hot encoding feature explosions (curse of dimensionality), causing memory overload.",
            "confidence_score": 0.90
        }

class MixedTextDetector(BaseDetector):
    """Detects columns where text rows contain a mix of alphabetic, digits, and special characters."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        text_cols = df.select_dtypes(include=["object"]).columns
        mixed_cols = {}
        
        for col in text_cols:
            non_nulls = df[col].dropna().astype(str)
            if len(non_nulls) == 0:
                continue
                
            # Count values with both letters and numbers
            is_mixed = non_nulls.str.contains(r"[A-Za-z]") & non_nulls.str.contains(r"[0-9]")
            mixed_count = int(is_mixed.sum())
            ratio = mixed_count / len(non_nulls)
            
            if ratio > 0.25: # If > 25% of string cells are mixed
                mixed_cols[col] = {
                    "mixed_cell_count": mixed_count,
                    "mixed_ratio": float(ratio)
                }
                
        problem = None
        solution = None
        if len(mixed_cols) > 0:
            problem = f"Mixed alphanumeric patterns found in text columns: {list(mixed_cols.keys())}."
            solution = "Normalize text casing, strip trailing units (e.g. convert '120usd' to float), or extract numeric markers."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "mixed_columns": mixed_cols
            },
            "explanation": "Mixed string structures indicate units appended to integers, or concatenated labels that confuse encoders.",
            "confidence_score": 0.80
        }

class ExtraSpacesDetector(BaseDetector):
    """Detects leading, trailing, or duplicate whitespaces in text columns."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        text_cols = df.select_dtypes(include=["object"]).columns
        space_cols = {}
        
        for col in text_cols:
            non_nulls = df[col].dropna().astype(str)
            if len(non_nulls) == 0:
                continue
                
            # Match leading/trailing spaces or double spaces in between
            has_spaces = non_nulls.str.contains(r"^\s+|\s+$|\s{2,}")
            space_count = int(has_spaces.sum())
            
            if space_count > 0:
                space_cols[col] = {
                    "affected_rows": space_count,
                    "affected_ratio": float(space_count / len(non_nulls))
                }
                
        problem = None
        solution = None
        if len(space_cols) > 0:
            problem = f"Trailing or consecutive whitespaces found in text columns: {list(space_cols.keys())}."
            solution = "Apply Text Normalization to trim leading/trailing spaces and collapse duplicate spaces."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "space_anomalies": space_cols
            },
            "explanation": "Invisible spaces cause categorization mismatches (e.g., ' Yes' vs 'Yes' are treated as two distinct groups).",
            "confidence_score": 1.0
        }

class InvalidDateDetector(BaseDetector):
    """Detects text fields containing date-like entries with parsing errors."""
    
    def detect(self, df: pd.DataFrame) -> dict:
        text_cols = df.select_dtypes(include=["object"]).columns
        invalid_dates = {}
        
        for col in text_cols:
            # Run simple check: does column name look like a date or contain date values
            col_lower = col.lower()
            is_date_col = "date" in col_lower or "time" in col_lower or "timestamp" in col_lower
            
            non_nulls = df[col].dropna().astype(str)
            if len(non_nulls) < 5:
                continue
                
            # Attempt to parse date
            parsed = pd.to_datetime(non_nulls, errors="coerce", format="mixed")
            failures = int(parsed.isnull().sum())
            successes = len(non_nulls) - failures
            
            # If it is a date column and has failures, or looks like mostly date format (>50% successes) but has some failures
            if (is_date_col and failures > 0) or (successes / len(non_nulls) > 0.50 and failures > 0):
                invalid_dates[col] = {
                    "total_samples": len(non_nulls),
                    "failed_parses": failures,
                    "failure_ratio": float(failures / len(non_nulls))
                }
                
        problem = None
        solution = None
        if len(invalid_dates) > 0:
            problem = f"Failed date parsings in column(s): {list(invalid_dates.keys())}."
            solution = "Clean date strings, remove garbage text values, or standardize timezone settings."
            
        return {
            "problem": problem,
            "solution": solution,
            "statistics": {
                "invalid_date_columns": invalid_dates
            },
            "explanation": "Mismatched formats (MM/DD/YYYY vs YYYY-MM-DD) or garbage date values drop entries when cast to datetime.",
            "confidence_score": 0.90
        }
