import os
from dotenv import load_dotenv
from core.llm import get_llm_provider, GeminiProvider, OpenAIProvider
from core.ai import (
    explain_cleaning_steps,
    dataset_summary,
    ml_readiness_explanation,
    feature_engineering_suggestions,
    recommended_algorithms,
    answer_dataset_questions
)

load_dotenv()

def run_ai_tests():
    print("=== Testing LLM Provider Configuration ===")
    provider = get_llm_provider()
    
    if provider:
        print(f"Detected Active LLM Provider: {provider.__class__.__name__}")
    else:
        print("No active LLM Provider detected (GEMINI_API_KEY is empty). Testing local fallback explainers.")
    print()

    # Generate test variables
    mock_history = [
        {"action": "Dropped 10 duplicate rows", "affected": "Observations"},
        {"action": "Imputed null values with median", "affected": "col_age"}
    ]
    mock_stats = {
        "rows": 100,
        "columns": 5,
        "null_percentage": 5.0,
        "duplicate_count": 0,
        "total_outliers": 2
    }
    mock_schema = [
        {"Column Name": "age", "Data Type": "float64"},
        {"Column Name": "churn", "Data Type": "object"},
        {"Column Name": "signup_date", "Data Type": "object"}
    ]

    print("=== 1. Testing explain_cleaning_steps ===")
    explanation = explain_cleaning_steps(mock_history, mock_stats)
    print(explanation[:250] + "\n...")
    assert len(explanation) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== 2. Testing dataset_summary ===")
    summary = dataset_summary(mock_stats)
    print(summary[:250] + "\n...")
    assert len(summary) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== 3. Testing ml_readiness_explanation ===")
    readiness = ml_readiness_explanation(78.5, {"MissingValues": "Found 5 null cells in column 'age'"})
    print(readiness[:250] + "\n...")
    assert len(readiness) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== 4. Testing feature_engineering_suggestions ===")
    features = feature_engineering_suggestions(mock_schema)
    print(features[:250] + "\n...")
    assert len(features) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== 5. Testing recommended_algorithms ===")
    algos = recommended_algorithms(mock_schema, "classification")
    print(algos[:250] + "\n...")
    assert len(algos) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== 6. Testing answer_dataset_questions ===")
    answer = answer_dataset_questions("Identify age outliers", {"age": {"min": 1, "max": 108}})
    print(answer[:250] + "\n...")
    assert len(answer) > 0, "Failed: empty output"
    print("Pass.")
    print()

    print("=== All AI Prompts and Providers Checked Successfully ===")

if __name__ == "__main__":
    run_ai_tests()
