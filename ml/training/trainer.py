import os
import json
import joblib
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from ml.preprocessing.text_normalizer import normalize_text_for_ml
from backend.app.core.logging import app_logger

MODEL_PATH = "ml/saved_models/doc_classifier.joblib"
METRICS_PATH = "ml/saved_models/metrics.json"

# Representative Medical Text Dataset for 6 classes
TRAINING_SAMPLES = [
    # Clinical Report
    ("Patient admitted with acute chest discomfort. Physical exam shows regular rate, clear breath sounds. Past medical history includes hyperlipidemia and coronary artery disease.", "clinical_report"),
    ("Subjective: 54-year-old male presents for follow-up evaluation. Objective: Vital signs stable, blood pressure 128/82. Plan: Continue current regimen and monitor.", "clinical_report"),
    ("Discharge summary: Patient diagnosed with community-acquired pneumonia, responded favorably to course of IV antibiotics, discharged home in stable condition.", "clinical_report"),
    ("Emergency Department physician notes: Triage assessment completed. Patient reports sudden onset of lower abdominal pain. Abdominal palpation reveals mild tenderness.", "clinical_report"),
    ("Operative report: Procedure performed: Laparoscopic appendectomy. Findings: Inflamed appendix removed without complication. Estimated blood loss minimal.", "clinical_report"),
    ("Consultation note: Cardiology consult requested for evaluation of sinus bradycardia. EKG reveals sinus rhythm at 48 bpm with normal PR interval.", "clinical_report"),

    # Laboratory Report
    ("Complete blood count CBC: Hemoglobin 14.2 g/dL, Hematocrit 42%, Platelet count 250,000 /mcL, White blood cell count 6.5 x10^3/mcL. Reference ranges within normal limits.", "laboratory_report"),
    ("Lipid panel profile: Total cholesterol 215 mg/dL, Triglycerides 160 mg/dL, HDL cholesterol 45 mg/dL, LDL cholesterol 138 mg/dL. Specimen fasting blood draw.", "laboratory_report"),
    ("Urinalysis test report: Specific gravity 1.020, pH 6.0, Leukocyte esterase negative, Nitrite negative, Protein trace, Glucose negative, Ketones negative.", "laboratory_report"),
    ("Comprehensive metabolic panel CMP: Serum sodium 140 mEq/L, Potassium 4.2 mEq/L, Blood urea nitrogen BUN 16 mg/dL, Serum creatinine 0.9 mg/dL, eGFR > 60.", "laboratory_report"),
    ("Thyroid function blood test: Thyroid stimulating hormone TSH 2.45 mIU/L, Free T4 1.1 ng/dL. Normal baseline hormonal values.", "laboratory_report"),
    ("Coagulation study: Prothrombin time PT 11.8 seconds, International normalized ratio INR 1.02, Partial thromboplastin time PTT 28 seconds.", "laboratory_report"),

    # Medical Research
    ("Abstract: A randomized double-blind placebo-controlled clinical trial investigating the efficacy of novel monoclonal antibodies in reducing arterial plaque inflammation.", "medical_research"),
    ("Methodology: Cohort study involving 1,200 participants across five academic medical centers. Primary endpoint assessed five-year all-cause mortality using Kaplan-Meier curves.", "medical_research"),
    ("Results and Discussion: Statistical significance achieved with p-value < 0.001. Confidence interval 95% CI [1.14, 2.38]. Peer-reviewed findings published under journal DOI 10.1016.", "medical_research"),
    ("Introduction: Genomic variations in drug-metabolizing enzymes significantly influence therapeutic pharmacokinetics. Here we characterize single nucleotide polymorphisms.", "medical_research"),
    ("Meta-analysis of systemic reviews: Forest plots demonstrate aggregated relative risk reduction of 18% across 14 eligible international randomized controlled trials.", "medical_research"),
    ("Conclusion: Further translational investigation is warranted to elucidate the molecular signaling cascade governing cellular apoptosis in ischemic models.", "medical_research"),

    # Insurance Document
    ("Health insurance claim form: CMS-1500 medical billing. Policy ID: POL-883921. Subscriber name, group health number, copay amount $25.00.", "insurance_document"),
    ("Prior authorization request: Covered benefit eligibility determination for specialty pharmaceutical. Deductible satisfied, out-of-pocket maximum $3,500.", "insurance_document"),
    ("Explanation of benefits EOB: Date of service, billed charges $1,450.00, allowed amount $820.00, insurer payment $656.00, patient responsibility $164.00.", "insurance_document"),
    ("Medicare Advantage enrollment agreement: Summary of benefits, network provider coverage, prescription drug Part D tier formulary copayments.", "insurance_document"),
    ("Health maintenance organization policy terms: Primary care physician referral requirement, in-network vs out-of-network deductible schedules.", "insurance_document"),
    ("Workers compensation medical claim denial appeal: Documented injury report, employer carrier policy endorsement number WC-901284.", "insurance_document"),

    # General Health Information
    ("Understanding Healthy Sleep Hygiene: Tips for getting better rest including avoiding caffeine before bed, maintaining a dark cool room, and daily exercise.", "general_health_information"),
    ("Patient education guide on dietary nutrition: The benefits of consuming whole grains, fresh vegetables, lean proteins, and staying hydrated throughout the day.", "general_health_information"),
    ("Managing everyday stress: Mindfulness techniques, meditation, deep breathing exercises, and spending time outdoors can improve mental well-being.", "general_health_information"),
    ("Hydration facts for families: How drinking water supports kidney function, regulates body temperature, and prevents dehydration during physical activity.", "general_health_information"),
    ("Sun safety pamphlet: Wearing broad-spectrum SPF 30 sunscreen, wearing protective hats, and seeking shade during midday hours protects skin health.", "general_health_information"),
    ("Basic ergonomics at the desk: Adjusting chair height, maintaining posture, and taking stretching breaks prevents repetitive strain injuries.", "general_health_information"),

    # Other
    ("Invoice statement for medical equipment delivery: Purchased 10 ergonomic hospital beds, freight delivery tracking number 991283.", "other"),
    ("Information technology software license agreement: Terms of service and cloud server hosting uptime guarantees for hospital intranet.", "other"),
    ("Employee parking permit registration guidelines: Facilities maintenance schedule and building security badge issuance protocol.", "other"),
    ("Conference room reservation schedule: Department quarterly administrative meeting agenda and catering order confirmation.", "other"),
    ("Vendor supplies contract: Disposable nitrile gloves, sanitary towels, and cleaning supplies shipping logistics.", "other"),
    ("Hospital cafeteria weekly menu: Daily soup specials, sandwich counter hours, and holiday scheduling announcements.", "other")
]


def train_and_persist_model() -> Dict[str, Any]:
    """Trains TF-IDF + Logistic Regression document classifier, measures genuine metrics, and persists artifacts."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    texts = [normalize_text_for_ml(s[0]) for s in TRAINING_SAMPLES]
    labels = [s[1] for s in TRAINING_SAMPLES]

    # Split into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)),
        ("clf", LogisticRegression(C=1.0, max_iter=200, random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate on holdout test set
    y_pred = pipeline.predict(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    metrics = {
        "model_type": "TF-IDF + LogisticRegression",
        "model_version": "1.0.0",
        "classes": sorted(list(set(labels))),
        "training_samples_count": len(X_train),
        "test_samples_count": len(X_test),
        "measured_accuracy": round(acc, 4),
        "measured_precision": round(prec, 4),
        "measured_recall": round(rec, 4),
        "measured_f1_score": round(f1, 4)
    }

    # Persist model and metrics
    joblib.dump(pipeline, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    app_logger.info(f"Trained ML Document Classifier. Accuracy: {metrics['measured_accuracy']:.2f}, F1: {metrics['measured_f1_score']:.2f}")
    return metrics


if __name__ == "__main__":
    result = train_and_persist_model()
    print(json.dumps(result, indent=2))
