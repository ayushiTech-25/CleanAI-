import pandas as pd
import numpy as np
from core.base import BaseCleaner
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer

class MeanImputationCleaner(BaseCleaner):
    """Fills missing numerical values with the mean of the column."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        logs = []
        
        for col in cols:
            if col in df_clean.columns:
                null_count = df_clean[col].isnull().sum()
                if null_count > 0:
                    mean_val = float(df_clean[col].mean())
                    df_clean[col] = df_clean[col].fillna(mean_val)
                    logs.append(f"Filled {null_count} nulls in '{col}' with mean {mean_val:.2f}")
                    
        return df_clean, {
            "strategy": "Mean Imputation",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 1.0
        }

class MedianImputationCleaner(BaseCleaner):
    """Fills missing numerical values with the median of the column."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        logs = []
        
        for col in cols:
            if col in df_clean.columns:
                null_count = df_clean[col].isnull().sum()
                if null_count > 0:
                    median_val = float(df_clean[col].median())
                    df_clean[col] = df_clean[col].fillna(median_val)
                    logs.append(f"Filled {null_count} nulls in '{col}' with median {median_val:.2f}")
                    
        return df_clean, {
            "strategy": "Median Imputation",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 1.0
        }

class ModeImputationCleaner(BaseCleaner):
    """Fills missing categorical/object values with the mode of the column."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["object", "category"]).columns
        logs = []
        
        for col in cols:
            if col in df_clean.columns:
                null_count = df_clean[col].isnull().sum()
                if null_count > 0:
                    mode_series = df_clean[col].mode()
                    if not mode_series.empty:
                        mode_val = mode_series.iloc[0]
                        df_clean[col] = df_clean[col].fillna(mode_val)
                        logs.append(f"Filled {null_count} nulls in '{col}' with mode '{mode_val}'")
                        
        return df_clean, {
            "strategy": "Mode Imputation",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 0.95
        }

class KNNImputationCleaner(BaseCleaner):
    """Fills missing values using Scikit-Learn's KNN Imputer."""
    
    def __init__(self, columns: list = None, n_neighbors: int = 5):
        self.columns = columns
        self.n_neighbors = n_neighbors
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        cols = [c for c in cols if df_clean[c].isnull().any()]
        
        logs = []
        if len(cols) > 0:
            imputer = KNNImputer(n_neighbors=self.n_neighbors)
            df_clean[cols] = imputer.fit_transform(df_clean[cols])
            logs.append(f"Applied KNN Imputation (k={self.n_neighbors}) to columns: {cols}")
            
        return df_clean, {
            "strategy": f"KNN Imputation (k={self.n_neighbors})",
            "modified_columns": cols,
            "logs": logs,
            "confidence_score": 0.88
        }

class DuplicateRemovalCleaner(BaseCleaner):
    """Removes identical duplicate rows from the dataset."""
    
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        before_rows = len(df)
        df_clean = df.drop_duplicates()
        after_rows = len(df_clean)
        removed = before_rows - after_rows
        
        logs = [f"Dropped {removed} duplicate rows. Rows remaining: {after_rows}."] if removed > 0 else ["No duplicates found."]
        
        return df_clean, {
            "strategy": "Duplicate Removal",
            "rows_removed": removed,
            "logs": logs,
            "confidence_score": 1.0
        }

class IQROutlierCleaner(BaseCleaner):
    """Clips outlier values in numerical columns using the 1.5 IQR bounds."""
    
    def __init__(self, columns: list = None, multiplier: float = 1.5):
        self.columns = columns
        self.multiplier = multiplier
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        logs = []
        
        for col in cols:
            q1 = df_clean[col].quantile(0.25)
            q3 = df_clean[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower_bound = q1 - self.multiplier * iqr
            upper_bound = q3 + self.multiplier * iqr
            
            # Count values to clip
            under_mask = df_clean[col] < lower_bound
            over_mask = df_clean[col] > upper_bound
            clip_count = under_mask.sum() + over_mask.sum()
            
            if clip_count > 0:
                df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
                logs.append(f"Clipped {clip_count} outlier values in '{col}' at range [{lower_bound:.2f}, {upper_bound:.2f}]")
                
        return df_clean, {
            "strategy": "IQR Outlier Clipping",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 0.90
        }

class ZScoreOutlierCleaner(BaseCleaner):
    """Drops rows containing values beyond a standard deviations limit (e.g. z-score > 3.0)."""
    
    def __init__(self, columns: list = None, threshold: float = 3.0):
        self.columns = columns
        self.threshold = threshold
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        
        rows_to_drop = pd.Series(False, index=df_clean.index)
        logs = []
        
        for col in cols:
            col_mean = df_clean[col].mean()
            col_std = df_clean[col].std()
            if col_std == 0 or pd.isna(col_std):
                continue
                
            z_scores = (df_clean[col] - col_mean) / col_std
            outliers = z_scores.abs() > self.threshold
            rows_to_drop = rows_to_drop | outliers
            
            outlier_count = outliers.sum()
            if outlier_count > 0:
                logs.append(f"Identified {outlier_count} outliers in '{col}' exceeding Z-score > {self.threshold}")
                
        dropped_count = int(rows_to_drop.sum())
        if dropped_count > 0:
            df_clean = df_clean[~rows_to_drop]
            logs.append(f"Dropped {dropped_count} row(s) containing Z-score outliers.")
            
        return df_clean, {
            "strategy": "Z-Score Outlier Drop",
            "rows_removed": dropped_count,
            "logs": logs,
            "confidence_score": 0.85
        }

class IsolationForestCleaner(BaseCleaner):
    """Filters outliers using Scikit-Learn's Isolation Forest algorithm."""
    
    def __init__(self, columns: list = None, contamination: float = 0.05):
        self.columns = columns
        self.contamination = contamination
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        logs = []
        
        # We need numerical columns without null values to train IsolationForest
        # We temporarily fill nulls with median to avoid crash
        temp_df = df_clean[cols].copy()
        for col in temp_df.columns:
            temp_df[col] = temp_df[col].fillna(temp_df[col].median())
            
        if len(cols) > 0 and len(df_clean) > 5:
            model = IsolationForest(contamination=self.contamination, random_state=42)
            preds = model.fit_predict(temp_df)
            
            outliers_mask = preds == -1
            outlier_count = int(outliers_mask.sum())
            
            if outlier_count > 0:
                df_clean = df_clean[~outliers_mask]
                logs.append(f"Isolation Forest dropped {outlier_count} outlier rows (contamination rate: {self.contamination*100}%)")
        else:
            outlier_count = 0
            logs.append("Insufficient data rows or columns to run Isolation Forest.")
            
        return df_clean, {
            "strategy": "Isolation Forest Filtering",
            "rows_removed": outlier_count,
            "logs": logs,
            "confidence_score": 0.82
        }

class ColumnRenamingCleaner(BaseCleaner):
    """Renames column headers using a dictionary mapping."""
    
    def __init__(self, columns_mapping: dict):
        self.columns_mapping = columns_mapping
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.rename(columns=self.columns_mapping)
        logs = [f"Renamed columns: {self.columns_mapping}"]
        
        return df_clean, {
            "strategy": "Column Renaming",
            "logs": logs,
            "confidence_score": 1.0
        }

class TextNormalizationCleaner(BaseCleaner):
    """Applies case normalizations and trims extra whitespace in text fields."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["object"]).columns
        logs = []
        
        for col in cols:
            # Keep nulls as nulls while normalizing actual text values.
            values = df_clean[col]
            df_clean[col] = values.where(
                values.isna(),
                values.astype(str).str.lower().str.strip().str.replace(r"\s+", " ", regex=True),
            )
            logs.append(f"Standardized lowercase casing & stripped spacing in column '{col}'")
            
        return df_clean, {
            "strategy": "Text Normalization",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 1.0
        }

class LabelStandardizationCleaner(BaseCleaner):
    """Standardizes target label category strings using a mapping dictionary."""
    
    def __init__(self, columns_mapping: dict):
        # Format: {"column_name": {"old_val": "new_val", ...}}
        self.columns_mapping = columns_mapping
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        logs = []
        
        for col, mapping in self.columns_mapping.items():
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].replace(mapping)
                logs.append(f"Standardized categorical values in '{col}' using mapping dictionary.")
                
        return df_clean, {
            "strategy": "Label Category Standardization",
            "logs": logs,
            "confidence_score": 0.98
        }

class FeatureScalingCleaner(BaseCleaner):
    """Scales numerical features using Standard Scaler (z-score) or MinMax Scaler."""
    
    def __init__(self, columns: list = None, method: str = "standard"):
        self.columns = columns
        self.method = method.lower()
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        
        # Filter columns that don't have nulls (StandardScaler throws errors on NaNs)
        cols = [c for c in cols if df_clean[c].notnull().all()]
        
        logs = []
        if len(cols) > 0:
            scaler = StandardScaler() if self.method == "standard" else MinMaxScaler()
            df_clean[cols] = scaler.fit_transform(df_clean[cols])
            logs.append(f"Applied {self.method.capitalize()} Scaling to features: {cols}")
        else:
            logs.append("No null-free numerical columns found to scale. Please impute first.")
            
        return df_clean, {
            "strategy": f"{self.method.capitalize()} Scaling",
            "modified_columns": cols,
            "logs": logs,
            "confidence_score": 1.0
        }

class L2NormalizationCleaner(BaseCleaner):
    """Applies row-wise L2 normalization to numerical columns."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["number"]).columns
        cols = [c for c in cols if df_clean[c].notnull().all()]
        
        logs = []
        if len(cols) > 0:
            normalizer = Normalizer(norm="l2")
            df_clean[cols] = normalizer.fit_transform(df_clean[cols])
            logs.append(f"Applied Row-Wise L2 Normalization to features: {cols}")
        else:
            logs.append("No null-free numerical columns found to normalize. Please impute first.")
            
        return df_clean, {
            "strategy": "L2 Normalization",
            "modified_columns": cols,
            "logs": logs,
            "confidence_score": 0.95
        }

class FeatureEncodingCleaner(BaseCleaner):
    """Transforms categorical text features into numerical one-hot encoded variables."""
    
    def __init__(self, columns: list = None):
        self.columns = columns
        
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        df_clean = df.copy()
        cols = self.columns if self.columns else df_clean.select_dtypes(include=["object"]).columns
        
        logs = []
        if len(cols) > 0:
            # We use pandas get_dummies for simple, clear encoding returns
            df_clean = pd.get_dummies(df_clean, columns=cols, drop_first=True)
            logs.append(f"One-hot encoded categorical columns: {list(cols)}")
        else:
            logs.append("No categorical columns found to encode.")
            
        return df_clean, {
            "strategy": "One-Hot Feature Encoding",
            "modified_columns": list(cols),
            "logs": logs,
            "confidence_score": 1.0
        }
