# action.py
import os
import asyncio
from pydantic import BaseModel
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

class ActionInput(BaseModel):
    action_type: str
    tool_name: str
    arguments: dict

class ActionOutput(BaseModel):
    result: str

async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py", "--env-key", os.getenv("GEMINI_API_KEY")]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return str(result.content if hasattr(result, 'content') else result)

def take_action(act_input: ActionInput) -> ActionOutput:
    if act_input.action_type == "function_call":
        result = asyncio.run(call_mcp_tool(act_input.tool_name, act_input.arguments))
        return ActionOutput(result=f"[MCP Response] {result}")

    elif act_input.action_type in ["final_answer", "complete_run"]:
        # Get the content from arguments (e.g., answer field)
        response_text = act_input.arguments.get("answer", "")
        verified_type = verify_action_type_from_llm(response_text)

        if verified_type == "final_answer":
            return ActionOutput(result=f"[Final Answer] {response_text}")
        elif verified_type == "complete_run":
            return ActionOutput(result="[Complete] Logistics task finished.")
        else:
            return ActionOutput(result=f"[Unverified] {response_text}")

    return ActionOutput(result="[Error] Unknown action.")

def verify_action_type_from_llm(response: str) -> str:
    """
    Stub: Use an LLM to determine if the response is a 'final_answer' or 'complete_run'.
    Return either 'final_answer', 'complete_run', or 'unknown'.
    """
    # You would replace this with actual LLM verification logic
    if "task finished" in response.lower():
        return "complete_run"
    elif "answer" in response.lower():
        return "final_answer"
    return "unknown"

