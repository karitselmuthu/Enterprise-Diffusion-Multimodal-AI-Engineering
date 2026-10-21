"""Evidence-linked incident triage from text, image features and documents."""

from __future__ import annotations

from .document_parser import extract_document
from .image_processor import load_image, summarize_image
from .vision_encoder import cosine_similarity, encode_image, encode_text
from .vlm_backend import get_backend
from .temporal import active_terms

HIGH_TERMS = {"fire", "smoke", "explosion", "injury", "hazardous", "critical"}
MEDIUM_TERMS = {"leak", "alarm", "failure", "overheat", "pressure"}


def analyze_incident(*, text: str, image_bytes: bytes | None = None, document_bytes: bytes | None = None,
                     document_name: str | None = None, backend: str = "mock", model_path: str | None = None) -> dict:
    if len(text) > 20_000:
        raise ValueError("incident text exceeds 20,000 characters")
    if not text.strip() and image_bytes is None and document_bytes is None:
        raise ValueError("provide report text, an image, or a document")
    if document_bytes is not None and not document_name:
        raise ValueError("document_name is required with document_bytes")
    evidence = []
    if text.strip():
        evidence.append({"source": "report_text", "content": text.strip()[:1000]})
    document = None
    if document_bytes is not None:
        document = extract_document(document_bytes, document_name or "")
        if document["text"].strip():
            evidence.append({"source": "document_text", "content": document["text"].strip()[:1000], "method": document["method"]})
    combined = " ".join(item["content"] for item in evidence if item["source"] in {"report_text", "document_text"})
    terms, temporal_state = active_terms(combined)
    matched_high = sorted(HIGH_TERMS & terms)
    matched_medium = sorted(MEDIUM_TERMS & terms)
    severity = "high" if matched_high else "medium" if matched_medium else "undetermined"
    image_summary = None
    vlm = None
    similarity = None
    if image_bytes is not None:
        image = load_image(image_bytes)
        image_summary = summarize_image(image)
        evidence.append({"source": "image_pixels", "content": image_summary, "method": "rgb_statistics"})
        similarity = cosine_similarity(encode_image(image), encode_text(combined))
        selected = get_backend(backend, model_path=model_path)
        vlm = selected.infer(image_bytes if backend == "local" else image,
                             "Read the status shown in this image. Report only visible text; say unreadable if needed.")
        if backend == "local":
            evidence.append({"source": "vlm_output", "content": vlm["answer"][:1000],
                             "method": vlm["model"], "verification": "unverified_model_output"})
    elif backend != "mock":
        raise ValueError("local backend requires an image")
    findings = []
    if matched_high or matched_medium:
        findings.append({"claim": f"Text contains incident terms: {', '.join(matched_high + matched_medium)}", "sources": [item["source"] for item in evidence if item["source"] in {"report_text", "document_text"}]})
    if image_summary:
        findings.append({"claim": f"Image mean RGB is {image_summary['mean_rgb']}; color alone does not establish a hazard", "sources": ["image_pixels"]})
    if backend == "local" and vlm and vlm["answer"]:
        findings.append({"claim": f"Unverified model observation: {vlm['answer'][:300]}",
                         "sources": ["vlm_output"], "verification": "requires_human_review"})
    return {"severity": severity, "temporal_state": temporal_state, "findings": findings, "evidence": evidence, "document": document,
            "image_text_color_similarity": similarity, "vlm": vlm,
            "limitations": ["Severity is a keyword triage signal, not a safety decision.", "Mock VLM reports pixel statistics only." if backend == "mock" else "Local VLM text may be inaccurate; verify against source image."]}
