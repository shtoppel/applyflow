from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.application import Application
from app.schemas.gmail import GmailParsedEventOut
from app.services.application_status_service import ApplicationStatusService
from app.services.gmail_parser import GmailRuleParser
from app.services.gmail_service import GmailService, GmailServiceError

router = APIRouter(prefix="/gmail", tags=["gmail"])


def build_recruiting_query(companies: list[str]) -> str:
    base_terms = [
        '"bewerbung"',
        '"application"',
        '"interview"',
        '"eingangsbestätigung"',
        '"ihre bewerbung"',
        '"deine bewerbung"',
        '"talent acquisition"',
        '"recruiting"',
    ]

    company_terms = [f'"{company.strip()}"' for company in companies if company and company.strip()]
    positive_parts = base_terms + company_terms
    positive_query = " OR ".join(positive_parts)

    negative_query = (
        "-from:immobilienscout24.de "
        "-from:suchen.immowelt.de "
        "-from:sender.skyscanner.com "
        "-from:kleinanzeigen.de "
        "-from:info@mail.heyjobs.co "
        "-from:noreply@github.com "
        "-from:mailer-daemon@googlemail.com "
        "-from:postmaster "
        "-from:me "
        "-category:promotions "
        "-category:social "
        "-subject:angebot "
        "-subject:mietwohnung "
        "-subject:preise "
        "-subject:job-highlight "
        "-subject:verifikation "
        "-subject:security "
    )

    return f"({positive_query}) newer_than:60d {negative_query}"


@router.post("/debug/raw")
def debug_raw():
    service = GmailService()

    try:
        messages = service.get_recent_messages(max_results=5)
    except GmailServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return [
        {
            "from": m.get("from"),
            "subject": m.get("subject"),
            "snippet": m.get("snippet"),
            "body_preview": (m.get("body_text") or "")[:1000],
        }
        for m in messages
    ]


@router.post("/debug/parsed")
def debug_parsed(db: Session = Depends(get_db)):
    result = db.execute(select(Application.company)).scalars().all()
    target_companies = list({company for company in result if company})

    service = GmailService()
    query = build_recruiting_query(target_companies)

    try:
        messages = service.get_recent_messages(max_results=20, query=query)
    except GmailServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    parser = GmailRuleParser(target_companies=target_companies)

    output = []
    for msg in messages:
        parsed = parser.parse(
            sender=msg.get("from"),
            subject=msg.get("subject"),
            snippet=msg.get("snippet"),
            body=msg.get("body_text"),
        )

        output.append(
            {
                "from": msg.get("from"),
                "subject": msg.get("subject"),
                "snippet": msg.get("snippet"),
                "body_preview": (msg.get("body_text") or "")[:800],
                "event": parsed.event,
                "reason": parsed.reason,
                "company_name": parsed.company_name,
            }
        )

    return {
        "query": query,
        "count": len(output),
        "items": output,
    }


@router.post("/sync", response_model=list[GmailParsedEventOut])
def sync_gmail(db: Session = Depends(get_db)):
    result = db.execute(select(Application.company)).scalars().all()
    target_companies = list({company for company in result if company})

    service = GmailService()
    query = build_recruiting_query(target_companies)

    try:
        messages = service.get_recent_messages(max_results=20, query=query)
    except GmailServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    parser = GmailRuleParser(target_companies=target_companies)
    parsed_events: list[GmailParsedEventOut] = []

    for msg in messages:
        parsed = parser.parse(
            sender=msg.get("from"),
            subject=msg.get("subject"),
            snippet=msg.get("snippet"),
            body=msg.get("body_text"),
        )

        if parsed.event == "unknown":
            continue

        reason = parsed.reason
        if parsed.company_name:
            reason = f"{reason}; matched company: {parsed.company_name}"
        else:
            reason = f"{reason}; matched company: none"

        parsed_events.append(
            GmailParsedEventOut(
                gmail_message_id=msg.get("gmail_message_id", ""),
                thread_id=msg.get("thread_id"),
                from_=msg.get("from", ""),
                subject=msg.get("subject", ""),
                date=msg.get("date"),
                snippet=msg.get("snippet"),
                event=parsed.event,
                reason=reason,
            )
        )

    return parsed_events


@router.post("/sync-and-update")
def sync_and_update(db: Session = Depends(get_db)):
    applications = db.execute(select(Application)).scalars().all()
    target_companies = list({app.company for app in applications if app.company})

    service = GmailService()
    query = build_recruiting_query(target_companies)

    try:
        messages = service.get_recent_messages(max_results=20, query=query)
    except GmailServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    parser = GmailRuleParser(target_companies=target_companies)

    updated_items = []
    detected_items = []

    app_by_company = {}
    for app in applications:
        if app.company and app.company not in app_by_company:
            app_by_company[app.company] = app

    for msg in messages:
        parsed = parser.parse(
            sender=msg.get("from"),
            subject=msg.get("subject"),
            snippet=msg.get("snippet"),
            body=msg.get("body_text"),
        )

        if parsed.event == "unknown":
            continue

        detected_items.append(
            {
                "from": msg.get("from"),
                "subject": msg.get("subject"),
                "event": parsed.event,
                "company_name": parsed.company_name,
                "reason": parsed.reason,
            }
        )

        if not parsed.company_name:
            continue

        application = app_by_company.get(parsed.company_name)
        if not application:
            continue

        old_status = application.status
        changed = ApplicationStatusService.apply_status_if_allowed(application, parsed.event)

        if changed:
            updated_items.append(
                {
                    "application_id": application.id,
                    "company": application.company,
                    "position": application.position,
                    "old_status": old_status,
                    "new_status": application.status,
                    "email_subject": msg.get("subject"),
                    "event": parsed.event,
                }
            )

    if updated_items:
        db.commit()
    else:
        db.rollback()

    return {
        "detected_events": detected_items,
        "updated_count": len(updated_items),
        "updated_items": updated_items,
    }