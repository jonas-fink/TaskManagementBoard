import base64, datetime, json, os, time
from unittest.mock import patch

os.environ["CLERK_WEBHOOK_SECRET"] = "whsec_" + base64.b64encode(b"0" * 24).decode()

from fastapi.testclient import TestClient
from svix.webhooks import Webhook
from app.main import app
from app.api import webhooks

client = TestClient(app)


def post(event):
    body = json.dumps(event)
    ts = int(time.time())
    sig = Webhook(os.environ["CLERK_WEBHOOK_SECRET"]).sign("msg_1", datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc), body)
    return client.post("/api/webhooks/clerk", content=body, headers={
        "svix-id": "msg_1", "svix-timestamp": str(ts), "svix-signature": sig,
        "content-type": "application/json",
    })


def event(slug, status="active"):
    return {"type": "subscription.updated", "data": {
        "payer": {"organization_id": "org_1"},
        "items": [{"plan": {"slug": slug}, "status": status}],
    }}


def test():
    with patch.object(webhooks, "set_org_member_limit") as m:
        assert post(event("pro_tier")).status_code == 200
        m.assert_called_with("org_1", 1_000_000)  # pro -> unlimited

        m.reset_mock()
        assert post(event("free_tier")).status_code == 200
        m.assert_called_with("org_1", 2)          # downgrade -> free limit

        m.reset_mock()
        assert post(event("pro_tier", "ended")).status_code == 200
        m.assert_called_with("org_1", 2)          # expired pro -> free limit

    # bad signature is rejected
    r = client.post("/api/webhooks/clerk", content=json.dumps(event("pro_tier")),
                    headers={"svix-id": "x", "svix-timestamp": str(int(time.time())), "svix-signature": "v1,bogus"})
    assert r.status_code == 400, r.status_code
    print("ok")


if __name__ == "__main__":
    test()
