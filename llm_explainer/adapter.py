"""
Adapters to convert raw model outputs and SHAP values into the
structured evidence dictionary expected by the LLM explanation layer.

The key helper in this module is ``build_evidence_from_arrays``,
which assembles the discrete label, per-feature SHAP attributions,
feature names and values into a single dictionary. Optional
reference ranges, friendly names for laypersons and clinicians,
and a model card can be provided.
"""

from typing import Dict, Any, Optional, List, Sequence, Union
import numpy as np

Arrow = Union[str, None]

def _arrow_from_value(value: float, ref_low: Optional[float], ref_high: Optional[float]) -> Arrow:
    try:
        v = float(value)
    except Exception:
        return "?"
    if ref_low is None or ref_high is None:
        return "?"
    if v > ref_high:
        return "↑"
    if v < ref_low:
        return "↓"
    return "?"

def _ensure_seq(x) -> Sequence:
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (list, tuple)):
        return x
    raise ValueError("Expected list/tuple/np.ndarray.")

def build_evidence_from_arrays(
    label: str,
    shap_values: Sequence[float],
    feature_names: Sequence[str],
    instance_values: Sequence[float],
    ref_ranges: Optional[Dict[str, Dict[str, Any]]] = None,
    k: int = 5,
    names_parent: Optional[Dict[str, str]] = None,
    names_doctor: Optional[Dict[str, str]] = None,
    model_card: Optional[Dict[str, Any]] = None,
    glossary: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Convert arrays from your runtime into the evidence dict expected by the LLM layer.
    If a glossary is provided, inject human- and clinician-friendly metadata
    (names, descriptions, units, reference text) per feature.
    """
    sv = np.array(_ensure_seq(shap_values), dtype=float)
    fn = list(_ensure_seq(feature_names))
    xv = list(_ensure_seq(instance_values))
    if not (len(sv) == len(fn) == len(xv)):
        raise ValueError("Lengths of shap_values, feature_names, and instance_values must match.")

    idx = np.argsort(-np.abs(sv))[:k]
    top_features: List[Dict[str, Any]] = []
    for i in idx:
        raw = fn[i]
        shap_val = float(sv[i])
        val = xv[i]

        # defaults
        parent_name = names_parent.get(raw, raw) if names_parent else raw
        doctor_name = names_doctor.get(raw, raw) if names_doctor else raw
        parent_desc = ""
        doctor_desc = ""
        unit = ""
        ref_text = "—"
        low = None
        high = None

        # merge from glossary
        if glossary and raw in glossary:
            g = glossary[raw]
            parent_name = g.get("parent_name", parent_name)
            doctor_name = g.get("doctor_name", doctor_name)
            parent_desc = g.get("parent_desc", parent_desc)
            doctor_desc = g.get("doctor_desc", doctor_desc)
            unit = g.get("unit", unit)
            # allow glossary to carry a reference string
            if "ref" in g:
                ref_text = g["ref"]

        # merge/override ref from explicit ref_ranges if provided
        if ref_ranges and raw in ref_ranges:
            ref_text = ref_ranges[raw].get("ref", ref_text)
            low = ref_ranges[raw].get("low", None)
            high = ref_ranges[raw].get("high", None)

        direction = _arrow_from_value(val, low, high)

        top_features.append({
            "name_raw": raw,
            "name_parent": parent_name,
            "name_doctor": doctor_name,
            "desc_parent": parent_desc,   # NEW
            "desc_doctor": doctor_desc,   # NEW
            "unit": unit,                 # NEW
            "value": val,
            "ref": ref_text,
            "shap": shap_val,
            "dir": direction
        })

    evd: Dict[str, Any] = {"label": label, "top_features": top_features}
    if model_card:
        evd["model_card"] = model_card
    return evd
