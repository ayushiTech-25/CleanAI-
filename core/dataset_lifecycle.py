from __future__ import annotations

from collections.abc import MutableMapping
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from core.pipeline import cached_run_all_detections


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".parquet", ".tsv", ".feather"}


class DatasetLoadError(ValueError):
    """Raised when an uploaded file cannot be loaded as a tabular dataset."""


def load_dataset_file(uploaded_file: Any) -> pd.DataFrame:
    """Load one supported uploaded file into a non-empty DataFrame."""
    filename = str(getattr(uploaded_file, "name", ""))
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS))
        raise DatasetLoadError(f"Unsupported file type. Use: {supported}.")

    try:
        payload = uploaded_file.getvalue()
    except AttributeError as exc:
        raise DatasetLoadError("The uploaded file could not be read.") from exc
    if not payload:
        raise DatasetLoadError("The uploaded file is empty.")

    try:
        if extension in {".csv", ".tsv"}:
            separator = "\t" if extension == ".tsv" else ","
            last_error: Exception | None = None
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
                try:
                    return _validate_dataframe(
                        pd.read_csv(BytesIO(payload), sep=separator, encoding=encoding),
                        filename,
                    )
                except UnicodeDecodeError as exc:
                    last_error = exc
            raise DatasetLoadError(f"Unable to decode '{filename}' as a text file.") from last_error

        readers = {
            ".xlsx": pd.read_excel,
            ".xls": pd.read_excel,
            ".json": pd.read_json,
            ".parquet": pd.read_parquet,
            ".feather": pd.read_feather,
        }
        return _validate_dataframe(readers[extension](BytesIO(payload)), filename)
    except DatasetLoadError:
        raise
    except (pd.errors.EmptyDataError, ValueError) as exc:
        raise DatasetLoadError(f"'{filename}' does not contain a valid tabular dataset: {exc}") from exc
    except Exception as exc:
        raise DatasetLoadError(f"Unable to load '{filename}': {exc}") from exc


def _validate_dataframe(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    if df.empty or len(df.columns) == 0:
        raise DatasetLoadError(f"'{filename}' contains no rows or columns.")
    return df


def store_loaded_dataset(state: MutableMapping[str, Any], df: pd.DataFrame, filename: str) -> None:
    """Store a fresh dataset and reset all state derived from a previous dataset."""
    active_df = df.copy()
    state["dataset"] = active_df
    state["original_dataset"] = active_df.copy()
    state["dataset_name"] = filename
    state["dataset_history_stack"] = [(active_df.copy(), "Dataset Loaded")]
    state["redo_stack"] = []
    state["history"] = []
    invalidate_dataset_results(state)


def store_active_dataset(
    state: MutableMapping[str, Any],
    df: pd.DataFrame,
    action: str,
    affected: str = "Clean Pipeline Run",
    before_df: pd.DataFrame | None = None,
) -> None:
    """Commit a cleaned DataFrame while preserving the untouched original."""
    active_df = df.copy()
    state["dataset"] = active_df
    state.setdefault("dataset_history_stack", []).append((active_df.copy(), action))
    state.setdefault("redo_stack", []).clear()
    history_entry = {
        "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
        "action": action,
        "affected": affected,
        "rows_after": len(active_df),
        "columns_after": len(active_df.columns),
    }
    if before_df is not None:
        history_entry["rows_before"] = len(before_df)
        history_entry["columns_before"] = len(before_df.columns)
        history_entry["rows_changed"] = len(active_df) - len(before_df)
    state.setdefault("history", []).append(history_entry)
    invalidate_dataset_results(state)


def invalidate_dataset_results(state: MutableMapping[str, Any]) -> None:
    """Clear every result derived from the active dataset."""
    state["cached_ai_summary"] = None
    state["cached_ai_readiness"] = None
    state["analysis_results"] = {}
    state["report_results"] = {}


def analyze_active_dataset(state: MutableMapping[str, Any]) -> dict:
    """Run detection against the current active dataset and refresh its cache."""
    df = state.get("dataset")
    if df is None or df.empty:
        state["analysis_results"] = {}
        return {}
    reports = cached_run_all_detections(df)
    state["analysis_results"] = reports
    return reports