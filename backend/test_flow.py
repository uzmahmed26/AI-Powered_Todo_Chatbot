#!/usr/bin/env python
"""
Comprehensive test to verify the entire chat flow:
1. OpenAI API key validation
2. MCP tool registration
3. Database connectivity
4. Agent message processing
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()


async def test_openai_key():
    """Test 1: Verify OpenAI API key is loaded and valid format."""
    print("\n" + "="*60)
    print("TEST 1: OpenAI API Key Validation")
    print("="*60)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("[FAIL] FAILED: OPENAI_API_KEY not found in environment")
        return False

    print(f"[OK] API key found")
    print(f"  Length: {len(api_key)} characters")
    print(f"  Starts with: {api_key[:10]}...")
    print(f"  Ends with: ...{api_key[-10:]}")

    if not api_key.startswith("sk-"):
        print("[FAIL] API key doesn't start with 'sk-'")
        return False

    if len(api_key) < 50:
        print("[FAIL] API key too short")
        return False

    print("[PASS] API key format looks valid")
    return True


async def test_mcp_tools():
    """Test 2: Verify MCP tools are registered."""
    print("\n" + "="*60)
    print("TEST 2: MCP Tool Registration")
    print("="*60)

    try:
        from src.mcp_server.server import tool_registry

        tools = tool_registry.list_tools()
        print(f"[OK] Registered tools: {tools}")

        if "add_task" not in tools:
            print("[FAIL] FAILED: add_task tool not registered")
            return False

        # Test getting tool
        add_task_tool = tool_registry.get_tool("add_task")
        print(f"[OK] add_task tool retrieved: {add_task_tool}")

        # Get schemas
        schemas = tool_registry.get_all_schemas()
        print(f"[OK] Total tool schemas: {len(schemas)}")

        print("[PASS] PASSED: MCP tools registered correctly")
        return True

    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_database():
    """Test 3: Verify database connectivity."""
    print("\n" + "="*60)
    print("TEST 3: Database Connectivity")
    print("="*60)

    try:
        from src.database.engine import async_engine
        from sqlalchemy import text

        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"[OK] Database query result: {row}")

        # Check tables exist
        async with async_engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"[OK] Database tables: {tables}")

            required_tables = {"tasks", "conversations", "messages"}
            missing = required_tables - set(tables)

            if missing:
                print(f"[FAIL] FAILED: Missing tables: {missing}")
                return False

        print("[PASS] PASSED: Database connection and schema verified")
        return True

    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent():
    """Test 4: Verify agent can process a simple message."""
    print("\n" + "="*60)
    print("TEST 4: OpenAI Agent Message Processing")
    print("="*60)

    try:
        from src.agent.agent import TodoAgent

        agent = TodoAgent(user_id="test-user")
        print(f"[OK] Agent initialized")
        print(f"  User ID: {agent.user_id}")
        print(f"  Model config: {agent.model_config}")
        print(f"  System prompt length: {len(agent.system_prompt)} chars")

        # Test a simple message (not invoking tools)
        test_message = "Hello! Can you help me manage my todos?"
        print(f"\n  Testing message: '{test_message}'")

        result = await agent.process_message(
            message=test_message,
            conversation_history=[]
        )

        print(f"\n  Agent response:")
        print(f"    Success: {result.get('success')}")
        response = result.get('response', '')
        print(f"    Response length: {len(response)} chars")
        print(f"    Tool calls: {len(result.get('tool_calls', []))}")
        if response:
            print(f"    Response preview: {response[:150]}...")

        if not result.get("success"):
            print(f"[FAIL] FAILED: Agent returned success=False")
            return False

        if not result.get("response"):
            print(f"[FAIL] FAILED: Agent returned empty response")
            return False

        print("[PASS] PASSED: Agent processed message successfully")
        return True

    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():

    """Run all tests."""

    print("\n" + "="*60)

    print("PHASE III TODO CHATBOT - COMPREHENSIVE FLOW TEST")

    print("="*60)



    results = []



    # Run tests

    results.append(("OpenAI Key", await test_openai_key()))

    results.append(("MCP Tools", await test_mcp_tools()))

    results.append(("Database", await test_database()))

    results.append(("Agent", await test_agent()))



    # Summary

    print("\n" + "="*60)

    print("TEST SUMMARY")

    print("="*60)



    for name, passed in results:

        status = "[PASS] PASSED" if passed else "[FAIL] FAILED"

        print(f"{status}: {name}")



    total = len(results)

    passed = sum(1 for _, p in results if p)



    print(f"\nTotal: {passed}/{total} tests passed")



    if passed == total:

        print("\n[SUCCESS] ALL TESTS PASSED! Chat flow is ready.")

        return 0

    else:

        print("\n[FAIL] SOME TESTS FAILED. See details above.")

        return 1





if __name__ == "__main__":

    exit_code = asyncio.run(main())

    sys.exit(exit_code)
