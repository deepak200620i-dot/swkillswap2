import json
from application import create_app
from utils import generate_token
from database import get_db

app = create_app()
client = app.test_client()

with app.app_context():
    # Get first two users
    db = get_db()
    user1 = db.execute("SELECT id, email, full_name FROM users LIMIT 1").fetchone()
    user2 = db.execute(
        "SELECT id, email, full_name FROM users LIMIT 1 OFFSET 1"
    ).fetchone()

    if user1 and user2:
        token1 = generate_token(user1["id"], user1["email"])

        # Test get conversations
        resp = client.get(
            "/api/chat/conversations", headers={"Authorization": f"Bearer {token1}"}
        )
        print(f"\n=== GET /api/chat/conversations ===")
        print(f"Status: {resp.status_code}")
        data = resp.get_json()
        print(f"Response: {json.dumps(data, indent=2)}")

        if data.get("conversations"):
            conv_id = data["conversations"][0]["id"]
            # Test get messages
            resp = client.get(
                f"/api/chat/{conv_id}/messages",
                headers={"Authorization": f"Bearer {token1}"},
            )
            print(f"\n=== GET /api/chat/{conv_id}/messages ===")
            print(f"Status: {resp.status_code}")
            data = resp.get_json()
            print(f"Response length: {len(json.dumps(data))}")
            print(f"First 500 chars: {json.dumps(data, indent=2)[:500]}...")
    else:
        print("Not enough users in database")
