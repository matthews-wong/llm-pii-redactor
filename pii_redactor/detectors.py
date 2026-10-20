"""Pattern detectors for values that must not leave the process."""

import re
from dataclasses import dataclass
from typing import Callable, Optional, Pattern

MIN_CARD_DIGITS = 13
MAX_CARD_DIGITS = 19
LUHN_MOD = 10


@dataclass(frozen=True)
class Detector:
    kind: str
    pattern: Pattern[str]
    validate: Optional[Callable[[str], bool]] = None


def luhn_valid(candidate: str) -> bool:
    digits = [int(c) for c in candidate if c.isdigit()]
    if not MIN_CARD_DIGITS <= len(digits) <= MAX_CARD_DIGITS:
        return False
    total = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % LUHN_MOD == 0


def _valid_ipv4(candidate: str) -> bool:
    return all(int(part) <= 255 for part in candidate.split("."))


# Order matters: secrets and cards are claimed before looser patterns such as phone.
DEFAULT_DETECTORS = (
    Detector("API_KEY", re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16})\b")),
    Detector("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    Detector("CARD", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), luhn_valid),
    Detector("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    Detector("IP", re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), _valid_ipv4),
    Detector("PHONE", re.compile(r"(?<![\w-])\+?\d{1,3}[ .-]?\(?\d{2,4}\)?[ .-]?\d{3,4}[ .-]?\d{3,4}\b")),
)
