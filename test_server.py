import httpx
import asyncio
import json

SERVER_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{SERVER_URL}/health"
CHAT_ENDPOINT_TEMPLATE = f"{SERVER_URL}/api/{{user_id}}/chat"

async def test_server():
    print("--- Starting Server Test ---")

    # 1. Test health endpoint
    print(f"Checking health endpoint: {HEALTH_ENDPOINT}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(HEALTH_ENDPOINT)
            response.raise_for_status() # Raise an exception for 4xx/5xx responses
            health_status = response.json()
            print(f"Health check successful: {health_status}")
            if health_status.get("status") != "healthy":
                print("WARNING: Health status is not 'healthy'.")
    except httpx.HTTPStatusError as e:
        print(f"Health check failed (HTTP error): {e}")
        return False
    except httpx.RequestError as e:
        print(f"Health check failed (Network error): {e}")
        return False
    except Exception as e:
        print(f"Health check failed (Other error): {e}")
        return False

    # 2. Test chat endpoint (requires a user_id and an actual chat API setup)
    print("\n--- Testing Chat Endpoint (Basic) ---")
    test_user_id = "test_user_123" # Placeholder user ID
    chat_url = CHAT_ENDPOINT_TEMPLATE.format(user_id=test_user_id)
    sample_message = "Hello, AI agent. What can you do?"

    try:
        async with httpx.AsyncClient() as client:
            # First, register or ensure user exists (if required by the API)
            # This step is highly dependent on the actual backend API.
            # For simplicity, we'll assume the /api/{user_id}/chat endpoint
            # handles user creation implicitly or that a user with test_user_id
            # can be used directly.

            # Send a POST request to the chat endpoint
            print(f"Sending message to chat endpoint: {chat_url}")
            chat_response = await client.post(
                chat_url,
                json={"message": sample_message},
                timeout=30 # Increased timeout for potential AI processing
            )
            chat_response.raise_for_status()
            chat_data = chat_response.json()
            print(f"Chat response successful: {json.dumps(chat_data, indent=2)}")

            # Basic validation of chat response
            if "response" in chat_data and isinstance(chat_data["response"], str):
                print("AI agent responded successfully with a message.")
                if not chat_data["response"]:
                    print("WARNING: AI agent responded with an empty message.")
            else:
                print("ERROR: Chat response does not contain expected 'response' field or it's not a string.")
                return False

    except httpx.HTTPStatusError as e:
        print(f"Chat request failed (HTTP error): {e.response.status_code} - {e.response.text}")
        print(f"Request details: {e.request}")
        return False
    except httpx.RequestError as e:
        print(f"Chat request failed (Network error): {e}")
        return False
    except Exception as e:
        print(f"Chat request failed (Other error): {e}")
        return False

    print("\n--- Server Test Completed Successfully! ---")
    return True

if __name__ == "__main__":
    asyncio.run(test_server())
