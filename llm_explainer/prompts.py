"""
Prompt templates and helper functions for generating human-readable
explanations from a machine-learning model's discrete prediction
and associated SHAP values. These templates are designed to
communicate the model's decision to both laypersons and
health-care professionals without offering medical diagnoses or
prescriptions.
"""

from typing import Dict, Any, List

PARENT_SYSTEM = (
    "You are a health communication assistant. "
    "Use only the evidence provided. "
    "No diagnosis or prescriptions. "
    "Write for non-experts at middle-school reading level. "
    "Explain why the model produced this label and suggest next-step actions "
    "that should be discussed with a clinician. If evidence is insufficient, say so."
)

DOCTOR_SYSTEM = (
    "You are a clinical decision explanation assistant. "
    "Use only the provided evidence; do not invent facts. "
    "Be quantitative, traceable, and aligned with the given SHAP attributions. "
    "Discuss potential limitations and confounders. "
    "No prescriptions. Output is for clinician review and does not replace judgment."
)

# llm_explainer/prompts.py (replace build_parent_user and build_doctor_user)

def build_parent_user(evidence: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"Model label: {evidence.get('label','UNKNOWN')}")
    lines.append("Key factors (ordered by impact, up to 5):")
    for f in evidence.get("top_features", [])[:5]:
        name = f.get("name_parent", f.get("name_raw", "feature"))
        value = f.get("value", "NA")
        unit = f.get("unit", "")
        ref = f.get("ref", "NA")
        direction = f.get("dir", "?")
        desc = f.get("desc_parent", "")
        unit_part = f" {unit}" if unit else ""
        desc_part = f" Meaning: {desc}" if desc else ""
        lines.append(f"- {name}{unit_part}: value {value} (ref {ref}), direction {direction}.{desc_part}")
    instructions = [
        "Please produce:",
        "1) One-sentence summary of the situation (avoid absolute statements).",
        "2) Why the model produced this label (map to the factors above using everyday language).",
        "3) Next steps the family can take (e.g., what to prepare when talking to the clinician, harmless lifestyle considerations).",
        "4) Closing disclaimer: this is an explanation, not a diagnosis; defer to clinical judgment."
    ]
    return "\n".join(lines + [""] + instructions)

def build_doctor_user(evidence: Dict[str, Any]) -> str:
    lines: List[str] = []
    label = evidence.get("label", "UNKNOWN")
    model_card = evidence.get("model_card", {})
    model_name = model_card.get("name", "UNKNOWN_MODEL")
    model_ver = model_card.get("version", "v0")
    lines.append(f"Discrete prediction (no probability provided): {label}")
    lines.append(f"Model: {model_name} ({model_ver})")
    lines.append("Top factors (with SHAP and direction):")
    for f in evidence.get("top_features", []):
        name = f.get("name_doctor", f.get("name_raw", "feature"))
        value = f.get("value", "NA")
        unit = f.get("unit", "")
        ref = f.get("ref", "NA")
        shap = f.get("shap", "NA")
        direction = f.get("dir", "?")
        desc = f.get("desc_doctor", "")
        unit_part = f" {unit}" if unit else ""
        desc_part = f" Note: {desc}" if desc else ""
        lines.append(
            f"- {name}{unit_part} = {value} (ref {ref}), SHAP={shap}, dir {direction}.{desc_part}"
        )
    instructions = [
        "Please produce:",
        "1) Interpretation of the discrete prediction and the primary drivers (factor-by-factor, mechanism hypotheses using general, conservative clinical knowledge).",
        "2) Potential confounders and model limitations (data bias, proxy variables, external validity).",
        "3) Suggested verification points for clinician review (tests to consider, follow-up indicators) without prescribing.",
        "4) Disclaimer: explanation based on local SHAP; does not replace clinical judgment."
    ]
    return "\n".join(lines + [""] + instructions)

