import re
from dataclasses import dataclass
from typing import Literal


GmailEventType = Literal[
    "in_review",
    "interview",
    "rejected",
    "accepted",
    "unknown",
]


@dataclass
class ParsedGmailEvent:
    event: GmailEventType
    company_name: str | None = None
    reason: str | None = None


class GmailRuleParser:
    IN_REVIEW_PATTERNS = [
        r"ihre bewerbung ist eingegangen",
        r"deine bewerbung ist eingegangen",
        r"vielen dank f[üu]r ihre bewerbung",
        r"vielen dank f[üu]r deine bewerbung",
        r"danke, dass du dir die zeit genommen hast, dich bei uns zu bewerben",
        r"danke f[üu]r ihre bewerbung",
        r"danke f[üu]r deine bewerbung",
        r"eingangsbest[aä]tigung",
        r"wir pr[üu]fen ihre unterlagen",
        r"wir pr[üu]fen deine unterlagen",
        r"schnellstm[oö]glich eine r[üu]ckmeldung",
        r"wie unser bewerbungsprozess abl[aä]uft",
        r"thank you for your application",
        r"application received",
        r"we are reviewing your application",
    ]

    INTERVIEW_PATTERNS = [
        r"wir m[oö]chten dich zu einem gespr[aä]ch einladen",
        r"wir m[oö]chten sie zu einem gespr[aä]ch einladen",
        r"einladung.{0,40}(gespr[aä]ch|interview)",
        r"bitte w[aä]hle einen termin",
        r"bitte teilen sie uns ihre verf[üu]gbarkeit mit",
        r"kennenlerngespr[aä]ch am",
        r"interview am",
        r"video-?call am",
        r"ladung zum gespr[aä]ch",
        r"schedule.{0,20}interview",
    ]

    REJECTED_PATTERNS = [
        r"\babsage\b",
        r"haben uns f[üu]r einen anderen kandidaten entschieden",
        r"nicht ber[üu]cksichtigen",
        r"rejection",
        r"not moving forward",
        r"unfortunately",
        r"leider",
    ]

    ACCEPTED_PATTERNS = [
        r"job offer",
        r"we are pleased to offer",
        r"vertragsangebot",
        r"willkommen im team",
        r"zusage f[üu]r die stelle",
        r"angebot f[üu]r die stelle",
    ]

    def __init__(self, target_companies: list[str] | None = None):
        self.target_companies = [c for c in (target_companies or []) if c]

    @staticmethod
    def _normalize(value: str | None) -> str:
        if not value:
            return ""
        value = value.lower().replace("\xa0", " ").strip()
        value = re.sub(r"\s+", " ", value)
        return value

    @staticmethod
    def _normalize_for_company(value: str | None) -> str:
        if not value:
            return ""
        value = value.lower().replace("\xa0", " ")
        value = re.sub(r"[^\w\s]", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    @staticmethod
    def _find_first_match(text: str, patterns: list[str]) -> str | None:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return pattern
        return None

    def _detect_company(
        self,
        sender: str | None,
        subject: str | None,
        snippet: str | None,
        body: str | None = None,
    ) -> str | None:
        full_text = self._normalize_for_company(
            " ".join(filter(None, [sender, subject, snippet, body]))
        )

        for company in self.target_companies:
            clean_company = self._normalize_for_company(company)
            clean_company = re.sub(r"\b(gmbh|ag|llc|inc|kg|mbh)\b", " ", clean_company)
            clean_company = re.sub(r"\s+", " ", clean_company).strip()

            if clean_company and clean_company in full_text:
                return company

        return None

    def parse(
        self,
        sender: str | None,
        subject: str | None,
        snippet: str | None,
        body: str | None = None,
    ) -> ParsedGmailEvent:
        full_text = self._normalize(" ".join(filter(None, [sender, subject, snippet, body])))
        detected_company = self._detect_company(sender, subject, snippet, body)

        checks = [
            ("accepted", self.ACCEPTED_PATTERNS),
            ("interview", self.INTERVIEW_PATTERNS),
            ("rejected", self.REJECTED_PATTERNS),
            ("in_review", self.IN_REVIEW_PATTERNS),
        ]

        for event_name, patterns in checks:
            match = self._find_first_match(full_text, patterns)
            if match:
                return ParsedGmailEvent(
                    event=event_name,  # type: ignore[arg-type]
                    company_name=detected_company,
                    reason=f"Matched rule: {match}",
                )

        return ParsedGmailEvent(
            event="unknown",
            company_name=detected_company,
            reason="No rule matched",
        )