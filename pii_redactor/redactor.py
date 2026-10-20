"""Replace detected values with stable placeholders and restore them later."""

import re
from dataclasses import dataclass, field
from typing import Dict, Sequence, Tuple

from .detectors import DEFAULT_DETECTORS, Detector

PLACEHOLDER_RE = re.compile(r"\[([A-Z_]+)_(\d+)\]")


@dataclass
class Redaction:
    """Result of redacting one text; `mapping` goes placeholder -> original."""

    text: str
    mapping: Dict[str, str] = field(default_factory=dict)


class Redactor:
    def __init__(self, detectors: Sequence[Detector] = DEFAULT_DETECTORS) -> None:
        self._detectors = tuple(detectors)

    def redact(self, text: str, mapping: Dict[str, str] = None) -> Redaction:
        """Redact `text`. Pass an existing mapping to keep placeholders stable
        across several texts of the same request."""
        mapping = {} if mapping is None else mapping
        spans = self._find_spans(text)
        by_value = {original: key for key, original in mapping.items()}
        counters: Dict[str, int] = {}
        for key in mapping:
            kind, number = PLACEHOLDER_RE.fullmatch(key).groups()
            counters[kind] = max(counters.get(kind, 0), int(number))

        out = []
        cursor = 0
        for start, end, kind in spans:
            value = text[start:end]
            if value not in by_value:
                counters[kind] = counters.get(kind, 0) + 1
                key = f"[{kind}_{counters[kind]}]"
                by_value[value] = key
                mapping[key] = value
            out.append(text[cursor:start])
            out.append(by_value[value])
            cursor = end
        out.append(text[cursor:])
        return Redaction("".join(out), mapping)

    def _find_spans(self, text: str) -> Sequence[Tuple[int, int, str]]:
        spans = []
        for detector in self._detectors:
            for match in detector.pattern.finditer(text):
                if detector.validate and not detector.validate(match.group()):
                    continue
                if any(match.start() < e and s < match.end() for s, e, _ in spans):
                    continue
                spans.append((match.start(), match.end(), detector.kind))
        return sorted(spans)


def restore(text: str, mapping: Dict[str, str]) -> str:
    """Put originals back. Unknown placeholders in model output stay as text."""
    return PLACEHOLDER_RE.sub(lambda m: mapping.get(m.group(), m.group()), text)
