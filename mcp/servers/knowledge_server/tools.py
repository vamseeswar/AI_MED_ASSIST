from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from mcp.registry import mcp_registry

# Curated Medical Knowledge Articles (Educational)
AUTHORITATIVE_KNOWLEDGE_BASE = {
    "kb-htn-01": {
        "id": "kb-htn-01",
        "title": "Hypertension: Pathophysiology and Clinical Guidelines",
        "category": "Cardiology",
        "summary": "Essential hypertension is sustained elevation of systemic arterial blood pressure.",
        "content": (
            "Hypertension is defined by the ACC/AHA guidelines as systolic blood pressure ≥ 130 mm Hg "
            "or diastolic blood pressure ≥ 80 mm Hg. Chronic elevated pressure contributes to vascular remodeling, "
            "left ventricular hypertrophy, and renal arteriolosclerosis. First-line lifestyle interventions "
            "include the DASH dietary pattern, sodium reduction (< 2300 mg/day), physical activity, and weight management."
        ),
        "source": "American College of Cardiology / AHA Guidelines"
    },
    "kb-t2d-02": {
        "id": "kb-t2d-02",
        "title": "Type 2 Diabetes Mellitus: Pathophysiological Overview",
        "category": "Endocrinology",
        "summary": "Metabolic disorder characterized by progressive insulin resistance and beta-cell secretory defect.",
        "content": (
            "Type 2 diabetes mellitus is characterized by hyperglycemia resulting from insulin resistance coupled "
            "with progressive insulin secretory defect. Diagnostic criteria include fasting plasma glucose ≥ 126 mg/dL, "
            "HbA1c ≥ 6.5%, or 2-hour oral glucose tolerance test ≥ 200 mg/dL. Long-term microvascular complications include "
            "retinopathy, nephropathy, and peripheral neuropathy."
        ),
        "source": "American Diabetes Association Standards of Care"
    },
    "kb-asthma-03": {
        "id": "kb-asthma-03",
        "title": "Asthma: Chronic Airway Inflammation and Management",
        "category": "Pulmonology",
        "summary": "Heterogeneous disease characterized by chronic airway inflammation and reversible airflow limitation.",
        "content": (
            "Asthma is characterized by recurrent episodes of wheezing, shortness of breath, chest tightness, and coughing. "
            "Key pathophysiological drivers include eosinophilic and neutrophilic airway inflammation, bronchial hyperresponsiveness, "
            "and mucus hypersecretion. Controller therapies emphasize inhaled corticosteroids to mitigate underlying inflammation."
        ),
        "source": "Global Initiative for Asthma (GINA) Report"
    }
}


class SearchKnowledgeParams(BaseModel):
    topic: str = Field(..., min_length=2)


def search_knowledge_tool(topic: str, user_context: Optional[Dict[str, Any]] = None):
    t_lower = topic.lower()
    matches = []
    for k_id, article in AUTHORITATIVE_KNOWLEDGE_BASE.items():
        if (t_lower in article["title"].lower() or
            t_lower in article["category"].lower() or
            t_lower in article["content"].lower()):
            matches.append({
                "article_id": article["id"],
                "title": article["title"],
                "category": article["category"],
                "summary": article["summary"],
                "source": article["source"]
            })
    return {
        "topic": topic,
        "count": len(matches),
        "articles": matches
    }


class GetKnowledgeArticleParams(BaseModel):
    article_id: str


def get_knowledge_article_tool(article_id: str, user_context: Optional[Dict[str, Any]] = None):
    article = AUTHORITATIVE_KNOWLEDGE_BASE.get(article_id)
    if not article:
        raise ValueError(f"Knowledge article '{article_id}' not found.")
    return article


def register_knowledge_server_tools():
    mcp_registry.register_tool(
        name="search_knowledge",
        server="knowledge_server",
        description="Search curated educational medical knowledge articles and guidelines.",
        func=search_knowledge_tool,
        param_model=SearchKnowledgeParams,
        read_only=True
    )
    mcp_registry.register_tool(
        name="get_knowledge_article",
        server="knowledge_server",
        description="Fetch a full educational medical article by its ID.",
        func=get_knowledge_article_tool,
        param_model=GetKnowledgeArticleParams,
        read_only=True
    )


register_knowledge_server_tools()
