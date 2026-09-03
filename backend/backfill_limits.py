"""Reconcile org membership limits with active Clerk subscriptions.

Run this after a missed/undelivered webhook:  PYTHONPATH=. python backfill_limits.py
"""
from app.core.clerk import clerk
from app.core.config import settings
from app.api.webhooks import PRO_TIER_SLUG

PRO_LIMIT = settings.PRO_TIER_MEMBERSHIP_LIMIT
FREE_LIMIT = settings.FREE_TIER_MEMBERSHIP_LIMIT


def pro_org_ids() -> set[str]:
    items = clerk.billing.list_subscription_items(payer_type="org", include_free=True, limit=500)
    return {
        i.payer.organization_id
        for i in items.data
        if i.plan and i.plan.slug == PRO_TIER_SLUG and str(i.status).endswith("ACTIVE")
        and i.payer and i.payer.organization_id
    }


def main():
    pro = pro_org_ids()
    for org in clerk.organizations.list(limit=500).data:
        want = PRO_LIMIT if org.id in pro else FREE_LIMIT
        if org.max_allowed_memberships == want:
            print(f"ok    {org.id} {org.name!r} limit={want}")
            continue
        clerk.organizations.update(organization_id=org.id, max_allowed_memberships=want)
        print(f"fixed {org.id} {org.name!r} {org.max_allowed_memberships} -> {want}")


if __name__ == "__main__":
    main()
