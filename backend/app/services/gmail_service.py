from __future__ import annotations

import base64
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.exceptions import TransportError


class GmailServiceError(Exception):
    pass


class GmailService:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self, token_path: str = "token.json"):
        self.token_path = token_path

    def _get_client(self):
        try:
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            return build("gmail", "v1", credentials=creds, cache_discovery=False)
        except Exception as exc:
            raise GmailServiceError(f"Failed to initialize Gmail client: {exc}") from exc

    @staticmethod
    def _parse_gmail_date(raw_value: str | None) -> datetime | None:
        if not raw_value:
            return None
        try:
            return parsedate_to_datetime(raw_value)
        except Exception:
            return None

    @staticmethod
    def _decode_base64url(data: str | None) -> str:
        if not data:
            return ""

        try:
            padding = "=" * (-len(data) % 4)
            decoded = base64.urlsafe_b64decode((data + padding).encode("utf-8"))
            return decoded.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def _strip_html(html: str) -> str:
        if not html:
            return ""

        html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
        html = re.sub(r"(?i)<br\s*/?>", "\n", html)
        html = re.sub(r"(?i)</p>|</div>|</li>|</tr>|</h1>|</h2>|</h3>", "\n", html)
        html = re.sub(r"(?s)<.*?>", " ", html)
        html = unescape(html)
        html = re.sub(r"[ \t]+", " ", html)
        html = re.sub(r"\n+", "\n", html)
        return html.strip()

    def _extract_body_text(self, payload: dict) -> str:
        plain_parts: list[str] = []
        html_parts: list[str] = []

        def walk(part: dict):
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data")

            if mime_type == "text/plain" and body_data:
                plain_parts.append(self._decode_base64url(body_data))
            elif mime_type == "text/html" and body_data:
                html_parts.append(self._decode_base64url(body_data))

            for child in part.get("parts", []) or []:
                walk(child)

        walk(payload)

        if plain_parts:
            text = "\n".join(x for x in plain_parts if x.strip())
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                return text

        if html_parts:
            html = "\n".join(x for x in html_parts if x.strip())
            text = self._strip_html(html)
            if text:
                return text

        raw_data = payload.get("body", {}).get("data")
        if raw_data:
            raw = self._decode_base64url(raw_data)
            text = self._strip_html(raw)
            return re.sub(r"\s+", " ", text).strip()

        return ""

    def get_recent_messages(self, max_results: int = 10, query: str | None = None) -> list[dict]:
        try:
            service = self._get_client()

            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=max_results,
                    q=query,
                )
                .execute()
            )

            message_refs = results.get("messages", [])
            parsed_messages: list[dict] = []

            for ref in message_refs:
                full_msg = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=ref["id"],
                        format="full",
                    )
                    .execute()
                )

                payload = full_msg.get("payload", {})
                headers = payload.get("headers", [])
                header_map = {h["name"]: h["value"] for h in headers}

                parsed_messages.append(
                    {
                        "gmail_message_id": full_msg.get("id"),
                        "thread_id": full_msg.get("threadId"),
                        "from": header_map.get("From", ""),
                        "subject": header_map.get("Subject", ""),
                        "date": self._parse_gmail_date(header_map.get("Date")),
                        "snippet": full_msg.get("snippet", ""),
                        "body_text": self._extract_body_text(payload),
                    }
                )

            return parsed_messages

        except TransportError as exc:
            raise GmailServiceError(
                "Could not reach Google servers. Check internet, VPN/proxy, firewall, or token refresh."
            ) from exc
        except Exception as exc:
            raise GmailServiceError(f"Failed to fetch Gmail messages: {exc}") from exc