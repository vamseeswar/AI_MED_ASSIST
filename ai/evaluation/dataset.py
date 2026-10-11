"""
Standard medical educational benchmark evaluation dataset for MedAssist AI.
Contains curated queries, mock document contexts with chunk IDs, and ground truth citations.
"""

from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    {
        "id": "eval-001",
        "query": "What are the common clinical symptoms of Type 2 Diabetes?",
        "ground_truth_chunk_ids": ["doc1_c1", "doc1_c2"],
        "documents": [
            {
                "id": "doc1_c1",
                "content": "Type 2 diabetes mellitus is characterized by hyperglycemia, insulin resistance, and relative impairment in insulin secretion. Common presenting symptoms include polydipsia (excessive thirst), polyuria (frequent urination), polyphagia (increased hunger), and unintended weight loss.",
                "metadata": {"doc_id": "doc-01", "document_name": "Endocrinology_Overview.pdf", "page": 3}
            },
            {
                "id": "doc1_c2",
                "content": "Additional non-specific symptoms of diabetes include persistent fatigue, blurred vision, slow-healing cutaneous sores, and frequent opportunistic infections.",
                "metadata": {"doc_id": "doc-01", "document_name": "Endocrinology_Overview.pdf", "page": 4}
            },
            {
                "id": "doc1_c3",
                "content": "Cardiovascular risk management requires blood pressure control, statin therapy, and smoking cessation counseling across primary care settings.",
                "metadata": {"doc_id": "doc-01", "document_name": "Endocrinology_Overview.pdf", "page": 12}
            }
        ]
    },
    {
        "id": "eval-002",
        "query": "How is Stage 1 hypertension defined in adults?",
        "ground_truth_chunk_ids": ["doc2_c1"],
        "documents": [
            {
                "id": "doc2_c1",
                "content": "According to the ACC/AHA clinical guidelines, Stage 1 hypertension is defined as a systolic blood pressure between 130 and 139 mmHg or a diastolic blood pressure between 80 and 89 mmHg on at least two separate clinical occasions.",
                "metadata": {"doc_id": "doc-02", "document_name": "Cardiology_Guidelines.pdf", "page": 2}
            },
            {
                "id": "doc2_c2",
                "content": "Stage 2 hypertension is classified when systolic blood pressure reaches 140 mmHg or higher, or diastolic pressure reaches 90 mmHg or higher.",
                "metadata": {"doc_id": "doc-02", "document_name": "Cardiology_Guidelines.pdf", "page": 3}
            }
        ]
    },
    {
        "id": "eval-003",
        "query": "What is the biological role of High-Density Lipoprotein (HDL) cholesterol?",
        "ground_truth_chunk_ids": ["doc3_c1"],
        "documents": [
            {
                "id": "doc3_c1",
                "content": "High-Density Lipoprotein (HDL) particles are responsible for reverse cholesterol transport, shuttling excess cholesterol from peripheral arterial tissues back to the liver for catabolism and biliary excretion.",
                "metadata": {"doc_id": "doc-03", "document_name": "Lipid_Metabolism.pdf", "page": 1}
            },
            {
                "id": "doc3_c2",
                "content": "Low-Density Lipoprotein (LDL) particles deposit cholesterol within the arterial intima, contributing directly to atherosclerotic plaque accumulation.",
                "metadata": {"doc_id": "doc-03", "document_name": "Lipid_Metabolism.pdf", "page": 2}
            }
        ]
    }
]
