"""
High-level helper to call the OpenAI Chat Completion API and generate
human-readable explanations for a machine-learning model's output.

This module exposes a single function, ``generate_explanations``, which
takes an evidence dictionary (see ``adapter.py`` for construction) and
returns two strings: one tailored to non-expert users (parents) and
another tailored to clinicians (doctor).
"""

import os
from typing import Optional, List
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from openai import OpenAI

from .prompts import (
    PARENT_SYSTEM,
    DOCTOR_SYSTEM,
    build_parent_user,
    build_doctor_user,
)

try:
    from .RAG.retriever import retrieve_context, format_contexts_for_prompt
except Exception:
    retrieve_context = None
    format_contexts_for_prompt = None

def _load_env() -> Tuple[str, str]:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Create a .env file with your key.")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    return api_key, model, base_url

def _chat(messages, model: str, api_key: str, base_url: Optional[str] = None, temperature: float = 0.2, max_tokens: int = 800) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()

def _validate_evidence(evd: Dict[str, Any]) -> None:
    if "label" not in evd:
        raise ValueError("Evidence missing 'label'.")
    if "top_features" not in evd:
        raise ValueError("Evidence missing 'top_features'.")
    if not isinstance(evd["top_features"], list) or len(evd["top_features"]) == 0:
        raise ValueError("'top_features' must be a non-empty list.")
    for i, f in enumerate(evd["top_features"]):
        if "name_raw" not in f and "name_parent" not in f and "name_doctor" not in f:
            raise ValueError(f"top_features[{i}] must include at least one of name_raw/name_parent/name_doctor.")
        if "value" not in f:
            raise ValueError(f"top_features[{i}] missing 'value'.")
        if "shap" not in f:
            raise ValueError(f"top_features[{i}] missing 'shap'.")
        if "dir" not in f:
            raise ValueError(f"top_features[{i}] missing 'dir' ('↑' or '↓' or '?').")

def generate_explanations(
    evidence: Dict[str, Any],
    rag_index_dir: Optional[str] = None,
    rag_top_k: int = 5
) -> Dict[str, str]:
    """
    If rag_index_dir is provided and valid, doctor-facing output will be grounded
    with retrieved passages from local PDFs.
    """
    api_key, model, base_url = _load_env()
    _validate_evidence(evidence)

    # Parent messages (no RAG)
    parent_user = build_parent_user(evidence)
    parent_messages = [
        {"role": "system", "content": PARENT_SYSTEM},
        {"role": "user", "content": parent_user},
    ]
    parent_text = _chat(parent_messages, model, api_key,base_url, temperature=0.2, max_tokens=700)

    # Doctor messages (with optional RAG)
    doctor_user = build_doctor_user(evidence)
    doctor_messages: List[Dict[str, str]] = [
        {"role": "system", "content": DOCTOR_SYSTEM},
    ]

    # If a RAG index exists and retriever is available, enrich context
    if rag_index_dir and retrieve_context and os.path.isdir(rag_index_dir):
        try:
            contexts = retrieve_context(rag_index_dir, evidence, top_k=rag_top_k)
            if contexts:
                ctx_text = format_contexts_for_prompt(contexts)
                doctor_messages.append({"role": "system", "content": ctx_text})
        except Exception as e:
            # Fail open: proceed without RAG if retrieval fails
            doctor_messages.append({"role": "system", "content": f"[RAG unavailable: {e}] Proceed with evidence only."})

    doctor_messages.append({"role": "user", "content": doctor_user})
    doctor_text = _chat(doctor_messages, model, api_key, base_url, temperature=0.2, max_tokens=900)

    return {"parent_text": parent_text, "doctor_text": doctor_text}
