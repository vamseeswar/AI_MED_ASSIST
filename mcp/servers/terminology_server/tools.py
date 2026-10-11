from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from mcp.registry import mcp_registry

MEDICAL_TERMINOLOGY_DICTIONARY = {
    "hypertension": {
        "term": "Hypertension",
        "definition": "A chronic medical condition in which the blood pressure in the arteries is persistently elevated.",
        "layperson_explanation": "High blood pressure. The force of blood pushing against artery walls is consistently too high.",
        "normal_reference": "Systolic < 120 mm Hg and Diastolic < 80 mm Hg",
        "clinical_significance": "Key modifiable risk factor for stroke, myocardial infarction, and renal disease."
    },
    "dyspnea": {
        "term": "Dyspnea",
        "definition": "Subjective experience of breathing discomfort consisting of qualitatively distinct sensations.",
        "layperson_explanation": "Shortness of breath or difficulty breathing.",
        "normal_reference": "Unlabored respiratory rate of 12-20 breaths per minute at rest.",
        "clinical_significance": "Cardinal symptom of cardiac and pulmonary diseases."
    },
    "hba1c": {
        "term": "HbA1c (Glycated Hemoglobin)",
        "definition": "Hemoglobin chemically linked to a sugar; reflects average blood glucose concentration over approximately 3 months.",
        "layperson_explanation": "A blood test showing average blood sugar control over the past 2 to 3 months.",
        "normal_reference": "Normal: < 5.7%; Prediabetes: 5.7%-6.4%; Diabetes: ≥ 6.5%",
        "clinical_significance": "Primary biomarker for diagnosing diabetes and monitoring glycemic control."
    },
    "troponin": {
        "term": "Cardiac Troponin",
        "definition": "Regulatory protein complex integral to cardiac muscle contraction.",
        "layperson_explanation": "A protein released into the bloodstream when heart muscle is injured or strained.",
        "normal_reference": "High-sensitivity troponin: < 14 ng/L (assay dependent)",
        "clinical_significance": "Sensitive and specific biomarker for myocardial injury and acute coronary syndromes."
    },
    "tachycardia": {
        "term": "Tachycardia",
        "definition": "Heart rate exceeding the normal resting rate, typically defined as greater than 100 beats per minute.",
        "layperson_explanation": "A rapid or racing heartbeat (over 100 beats a minute at rest).",
        "normal_reference": "Normal resting heart rate: 60-100 beats per minute",
        "clinical_significance": "Can be physiological (fever, exercise) or pathological (arrhythmias, sepsis)."
    }
}


class LookupMedicalTermParams(BaseModel):
    term: str = Field(..., min_length=2)


def lookup_medical_term_tool(term: str, user_context: Optional[Dict[str, Any]] = None):
    t_clean = term.strip().lower()

    # Exact or substring lookup
    for key, data in MEDICAL_TERMINOLOGY_DICTIONARY.items():
        if key == t_clean or t_clean in key or key in t_clean:
            return data

    return {
        "term": term,
        "definition": f"Clinical concept pertaining to '{term}'.",
        "layperson_explanation": f"Medical term related to {term}. Please consult medical literature for specialized subtype distinctions.",
        "normal_reference": "Variable by clinical laboratory and patient demographic.",
        "clinical_significance": "Refer to primary clinical documentation for contextual relevance."
    }


def register_terminology_server_tools():
    mcp_registry.register_tool(
        name="lookup_medical_term",
        server="terminology_server",
        description="Lookup medical terminology, clinical definition, and simple layperson translation.",
        func=lookup_medical_term_tool,
        param_model=LookupMedicalTermParams,
        read_only=True
    )


register_terminology_server_tools()
