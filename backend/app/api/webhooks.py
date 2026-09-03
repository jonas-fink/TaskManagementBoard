import json
import logging
from fastapi import APIRouter, Request, HTTPException, status
from svix.webhooks import Webhook
from app.core.config import settings
from app.core.clerk import clerk

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

PRO_TIER_SLUG = "pro_tier"
FREE_TIER_LIMIT = settings.FREE_TIER_MEMBERSHIP_LIMIT
PRO_TIER_LIMIT = settings.PRO_TIER_MEMBERSHIP_LIMIT


def set_org_member_limit(org_id: str, limit: int):
    clerk.organizations.update(
        organization_id=org_id,
        max_allowed_memberships=limit,
    )


def has_active_pro_plan(items: list) -> bool:
    return any(
        (item.get("plan") or {}).get("slug") == PRO_TIER_SLUG
        and item.get("status") in ("active", "past_due")
        for item in items
    )


@router.post("/clerk")
async def clerk_webhook(request: Request):
    payload = await request.body()

    if not settings.CLERK_WEBHOOK_SECRET:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Webhook secret not configured")
    try:
        Webhook(settings.CLERK_WEBHOOK_SECRET).verify(payload, dict(request.headers))
    except Exception:
        log.warning("rejected clerk webhook", exc_info=True)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid signature")

    event = json.loads(payload)
    event_type = event.get("type", "")
    data = event.get("data", {})

    if event_type.startswith("subscription."):
        org_id = (data.get("payer") or {}).get("organization_id")
        items = data.get("items", [])
        if not org_id:
            log.info("webhook %s: no organization_id (personal subscription?)", event_type)
            return {"received": True}
        limit = PRO_TIER_LIMIT if has_active_pro_plan(items) else FREE_TIER_LIMIT
        log.info(
            "webhook %s org=%s slugs=%s -> max_allowed_memberships=%s",
            event_type, org_id,
            [((i.get("plan") or {}).get("slug"), i.get("status")) for i in items],
            limit,
        )
        set_org_member_limit(org_id, limit)

    return {"received": True}
