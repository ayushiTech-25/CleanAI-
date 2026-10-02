from abc import ABC, abstractmethod
import pandas as pd

class BaseDetector(ABC):
    """
    Abstract base class for all data quality anomaly detectors.
    Follows Single Responsibility Principle (SRP).
    """
    
    @abstractmethod
    def detect(self, df: pd.DataFrame) -> dict:
        """
        Scans a DataFrame to search for anomalies.
        
        Returns a dict contract:
        {
            "problem": str or None,          # Description of the anomaly, or None if clean
            "solution": str or None,         # Suggested action, or None if clean
            "statistics": dict,              # Diagnostic metrics
            "explanation": str,              # Narrative description (placeholder)
            "confidence_score": float        # Value between 0.0 and 1.0
        }
        """
        pass

class BaseCleaner(ABC):
    """
    Abstract base class for all data cleaning repairs.
    Follows Open/Closed Principle (OCP).
    """

    @abstractmethod
    def clean(self, df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, dict]:
        """
        Executes cleaning repairs on the DataFrame.
        
        Returns:
            - pd.DataFrame: The cleaned DataFrame.
            - dict: Execution metadata summary.
        """
        pass
