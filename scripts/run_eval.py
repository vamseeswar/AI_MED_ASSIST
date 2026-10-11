"""
Standalone CLI script to execute the MedAssist AI RAG Evaluation benchmark.
Usage: python scripts/run_eval.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.evaluation.runner import run_evaluation
import json


def main():
    print("=" * 60)
    print("MEDASSIST AI — RAG EVALUATION BENCHMARK RUNNER")
    print("=" * 60)
    results = run_evaluation()
    print("\nAggregate Metrics:")
    print(json.dumps(results["aggregate_metrics"], indent=2))
    print(f"\nTotal Run Time: {results['total_eval_run_time_ms']} ms")
    print(f"Results stored in data/evaluation_results.json")


if __name__ == "__main__":
    main()
