"""Conservative clause-level time handling for the rule-based triage signal."""

from __future__ import annotations

import re

HAZARDS = {"fire", "smoke", "explosion", "injury", "hazardous", "critical", "leak", "alarm", "failure", "overheat", "pressure"}
RESOLVED = re.compile(r"\b(resolved|fixed|cleared|recovered|restored|normal|false positive|no longer active)\b", re.I)
PAST = re.compile(r"\b(yesterday|last week|last month|previously|historical|prior|earlier)\b", re.I)
CURRENT = re.compile(r"\b(now|currently|active|ongoing|again|recurring|recurred|reopened|still|today)\b", re.I)
NEGATED = re.compile(r"\b(no|without|denies)\s+(?:\w+\s+){0,2}(?:" + "|".join(sorted(HAZARDS)) + r")\b", re.I)
CLOCK = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")


def active_terms(text: str) -> tuple[set[str], str]:
    """Return terms supported as active; ambiguous historical-only claims stay unclassified.

    This is deliberately a narrow deterministic heuristic, not a timeline parser.
    """
    clauses = [part.strip() for part in re.split(r"[.!?;\n]+|\bbut\b|\bhowever\b", text.lower()) if part.strip()]
    events = []
    for index, clause in enumerate(clauses):
        clean = NEGATED.sub("", clause)
        terms = HAZARDS & set(re.findall(r"[a-z]+", clean))
        if not terms and not RESOLVED.search(clause):
            continue
        times = CLOCK.findall(clause)
        minute = int(times[-1][0]) * 60 + int(times[-1][1]) if times else None
        resolved = bool(RESOLVED.search(clause))
        current = bool(CURRENT.search(clause))
        past = bool(PAST.search(clause)) and not current
        events.append((index, minute, terms, resolved, current, past))
    if not events:
        return set(), "undetermined"
    # Explicit clock times supersede document order when the note contradicts itself.
    timed = [event for event in events if event[1] is not None]
    if timed:
        latest = max(timed, key=lambda event: (event[1], event[0]))
        events = [event for event in events if event[1] is None or event[1] >= latest[1]]
    current_resolution = [event for event in events if event[3] and (event[4] or event[1] is not None)]
    active = [event for event in events if event[2] and not event[3] and not event[5]]
    if current_resolution and (not active or max(event[0] for event in current_resolution) >= max(event[0] for event in active)):
        return set(), "resolved"
    if active:
        return set().union(*(event[2] for event in active)), "active"
    if any(event[3] for event in events):
        return set(), "resolved"
    return set(), "historical"
