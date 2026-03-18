import re


class GmailApplicationMatcher:
    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @classmethod
    def message_matches_company(
        cls,
        company_name: str,
        sender: str | None,
        subject: str | None,
        snippet: str | None,
    ) -> bool:
        if not company_name.strip():
            return False

        haystack = cls.normalize(" ".join(filter(None, [sender, subject, snippet])))
        needle = cls.normalize(company_name)

        return needle in haystack