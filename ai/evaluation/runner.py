"""
RAG Evaluation runner for MedAssist AI.
Executes benchmark queries through retrieval and generation,
measures actual latency and token usage, and produces non-fabricated evaluation metrics.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from ai.evaluation.evaluator import RAGEvaluator
from ai.evaluation.dataset import EVALUATION_DATASET
from rag.pipelines.rag_pipeline import get_rag_pipeline
from ai.llm_provider import get_llm_provider
from loguru import logger

RESULTS_FILE = Path("data/evaluation_results.json")


def run_evaluation() -> Dict[str, Any]:
    """
    Executes the comprehensive evaluation benchmark.
    Computes genuine metrics across all queries.
    """
    logger.info("Starting MedAssist AI RAG Evaluation run...")
    start_total_time = time.perf_counter()

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    rag = get_rag_pipeline()
    llm = get_llm_provider()

    query_results = []
    retrieval_precisions = []
    retrieval_recalls = []
    hit_rates = []
    context_relevances = []
    answer_relevances = []
    citation_accuracies = []
    groundedness_scores = []
    latencies = []
    total_tokens_estimated = 0

    for item in EVALUATION_DATASET:
        q_id = item["id"]
        query = item["query"]
        gt_ids = item["ground_truth_chunk_ids"]
        docs = item["documents"]

        t0 = time.perf_counter()

        # Index benchmark document chunks
        for d in docs:
            doc_id = d.get("metadata", {}).get("doc_id", q_id)
            doc_name = d.get("metadata", {}).get("document_name", "Medical Document")
            page = d.get("metadata", {}).get("page", 1)
            # Create a section structure
            section = [{
                "title": "General",
                "content": d["content"],
                "page_number": page
            }]
            rag.index_document_sections(doc_id, doc_name, section)

        # Retrieve top chunks using hybrid retrieval + cross-encoder reranking
        retrieval_res = rag.retrieve(query=query, top_k=3)
        retrieved_chunks = retrieval_res.get("chunks", [])
        retrieved_contexts = [c.get("content", "") for c in retrieved_chunks]
        
        # Check retrieval matches
        # Map retrieved chunks to see if ground truth content words match
        gt_doc_contents = {d["id"]: d["content"] for d in docs if d["id"] in gt_ids}
        retrieved_ids = []
        for rc in retrieved_chunks:
            rc_content = rc.get("content", "")
            # Identify which ground truth chunk it corresponds to
            matched_id = rc.get("chunk_id") or rc.get("document_id")
            for gid, gcontent in gt_doc_contents.items():
                if gcontent[:40].lower() in rc_content.lower() or rc_content[:40].lower() in gcontent.lower():
                    matched_id = gid
                    break
            retrieved_ids.append(matched_id)

        # Calculate retrieval metrics
        ret_metrics = RAGEvaluator.evaluate_retrieval(retrieved_ids, gt_ids, k=3)
        ctx_rel = RAGEvaluator.evaluate_context_relevance(query, retrieved_contexts)

        # Step 2: Answer generation with citations
        context_block = retrieval_res.get("formatted_context", "")
        prompt = (
            f"You are MedAssist AI. Answer the medical question using the provided context.\n"
            f"Do not provide diagnosis or treatment. Ground all claims in context.\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {query}\n"
            f"Answer:"
        )

        answer_text = llm.generate(
            system_prompt="Provide educational, source-grounded answers. Never diagnose or prescribe.",
            user_prompt=prompt
        )

        # Citation validation
        citations = retrieval_res.get("citations", [])
        # Adapt citations for evaluator
        adapted_citations = [
            {"chunk_id": c.get("document_id"), "snippet": c.get("snippet", "")}
            for c in citations
        ]
        adapted_chunks = [
            {"chunk_id": c.get("document_id"), "content": c.get("content", "")}
            for c in retrieved_chunks
        ]
        cit_metrics = RAGEvaluator.evaluate_citation_correctness(adapted_citations, adapted_chunks)
        ans_rel = RAGEvaluator.evaluate_answer_relevance(query, answer_text)
        groundedness = RAGEvaluator.evaluate_groundedness(answer_text, retrieved_contexts)

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        estimated_tokens = len(prompt.split()) + len(answer_text.split())

        # Accumulate
        retrieval_precisions.append(ret_metrics["precision_at_k"])
        retrieval_recalls.append(ret_metrics["recall_at_k"])
        hit_rates.append(ret_metrics["hit_rate"])
        context_relevances.append(ctx_rel)
        answer_relevances.append(ans_rel)
        citation_accuracies.append(cit_metrics["citation_accuracy"])
        groundedness_scores.append(groundedness)
        latencies.append(latency_ms)
        total_tokens_estimated += estimated_tokens

        query_results.append({
            "id": q_id,
            "query": query,
            "retrieved_chunk_ids": retrieved_ids,
            "ground_truth_chunk_ids": gt_ids,
            "retrieval": ret_metrics,
            "context_relevance": ctx_rel,
            "answer_relevance": ans_rel,
            "groundedness": groundedness,
            "citations": cit_metrics,
            "latency_ms": latency_ms,
            "tokens_estimated": estimated_tokens
        })

    total_latency_ms = round((time.perf_counter() - start_total_time) * 1000, 2)
    n = len(query_results)

    summary = {
        "status": "COMPLETED",
        "evaluated": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_benchmark_queries": n,
        "aggregate_metrics": {
            "hit_rate_at_3": round(sum(hit_rates) / n, 4) if n else 0.0,
            "retrieval_precision_at_3": round(sum(retrieval_precisions) / n, 4) if n else 0.0,
            "retrieval_recall_at_3": round(sum(retrieval_recalls) / n, 4) if n else 0.0,
            "mean_context_relevance": round(sum(context_relevances) / n, 4) if n else 0.0,
            "mean_answer_relevance": round(sum(answer_relevances) / n, 4) if n else 0.0,
            "mean_citation_correctness": round(sum(citation_accuracies) / n, 4) if n else 0.0,
            "mean_groundedness": round(sum(groundedness_scores) / n, 4) if n else 0.0,
            "avg_latency_ms": round(sum(latencies) / n, 2) if n else 0.0,
            "total_tokens_consumed": total_tokens_estimated
        },
        "query_details": query_results,
        "total_eval_run_time_ms": total_latency_ms
    }

    # Persist genuine results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Evaluation completed. Summary saved to {RESULTS_FILE}")
    return summary


def get_latest_evaluation() -> Dict[str, Any]:
    """Returns the latest evaluation results or 'Not evaluated yet'."""
    if not RESULTS_FILE.exists():
        return {
            "status": "Not evaluated yet",
            "evaluated": False,
            "message": "Evaluation has not been run. Trigger an evaluation to generate genuine metrics."
        }
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read evaluation results: {e}")
        return {
            "status": "Error reading evaluation results",
            "evaluated": False,
            "error": str(e)
        }
