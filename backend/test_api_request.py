#!/usr/bin/env python
"""Test API request directly to verify end-to-end flow."""
import httpx
import asyncio
import json


async def test_chat_api():
    """Send a test message to the chat API."""
    url = "http://localhost:8000/api/demo-user/chat"

    payload = {
        "message": "Add a task to buy groceries",
        "conversation_id": None
    }

    print("Sending POST request to:", url)
    print("Payload:", json.dumps(payload, indent=2))
    print("\nWaiting for response...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)

            print(f"\nStatus Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                print("\n[SUCCESS] Response received:")
                print(json.dumps(data, indent=2))

                # Check response structure
                if "response" in data:
                    print(f"\n[OK] Response text: {data['response'][:200]}...")
                if "tool_calls" in data:
                    print(f"[OK] Tool calls: {len(data.get('tool_calls', []))}")
                if "conversation_id" in data:
                    print(f"[OK] Conversation ID: {data.get('conversation_id')}")

                return True
            else:
                print(f"\n[FAIL] Error response:")
                print(response.text)
                return False

        except Exception as e:
            print(f"\n[FAIL] Request failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(test_chat_api())
    exit(0 if success else 1)
