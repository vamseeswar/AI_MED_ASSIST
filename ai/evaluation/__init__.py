"""
MedAssist AI evaluation module.
"""
from ai.evaluation.evaluator import RAGEvaluator
from ai.evaluation.dataset import EVALUATION_DATASET
from ai.evaluation.runner import run_evaluation, get_latest_evaluation

__all__ = [
    "RAGEvaluator",
    "EVALUATION_DATASET",
    "run_evaluation",
    "get_latest_evaluation"
]
