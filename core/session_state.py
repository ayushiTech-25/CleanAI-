from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any


def _initial_chat_messages() -> list[dict[str, str]]:
    return [
        {
            "role": "assistant",
            "text": "Hello! I am your CleanAI Co-pilot. Upload a dataset or load the sample data, and ask me to diagnose null values, search for outliers, or formulate imputation strategies.",
            "time": "Just Now",
        }
    ]


def initialize_session_state(state: MutableMapping[str, Any]) -> None:
    """Initialize CleanAI's shared session contract without overwriting user state."""
    defaults: dict[str, Any] = {
        "dataset": None,
        "original_dataset": None,
        "dataset_name": "",
        "dataset_history_stack": [],
        "redo_stack": [],
        "history": [],
        "chat_messages": _initial_chat_messages(),
        "cached_ai_summary": None,
        "cached_ai_readiness": None,
        "active_page": None,
        "cleaning_config": {},
        "settings_api_keys": {},
        "database_configuration": {},
        "quality_thresholds": {},
        "analysis_results": {},
        "report_results": {},
    }

    for key, value in defaults.items():
        if key not in state:
            state[key] = value