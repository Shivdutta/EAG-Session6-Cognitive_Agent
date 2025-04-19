# mcp_server.py
import os
import asyncio
import argparse
from google import genai
from config import llm
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Set the key as an environment variable
parser = argparse.ArgumentParser(description="Start the Logistics MCP server.")
parser.add_argument("--env-key", type=str, required=True, help="Gemini environment key (API key)")
args = parser.parse_args()
os.environ["GEMINI_API_KEY"] = args.env_key

async def call_llm(prompt: str) -> str:
    # Modify the prompt to include reasoning
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    reasoning_prompt = f"Please explain step-by-step how you arrived at the following conclusion: {prompt}"
    response = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=llm,
            contents=reasoning_prompt
        )
    )
    return response.text.strip()

mcp = FastMCP("Logistics MCP")

# === Core Logistics Tools ===
@mcp.tool()
async def suggest_kpis() -> dict:
    prompt = "Suggest 5 key performance indicators (KPIs) for warehouse and logistics operations."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def calculate_storage_utilization(total_capacity: int, used_capacity: int) -> dict:
    prompt = f"Calculate the storage utilization percentage when total capacity is {total_capacity} and used capacity is {used_capacity}. Provide step-by-step reasoning."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def optimize_picking_route(zone: str) -> dict:
    prompt = f"Suggest an efficient picking route strategy for a warehouse zone labeled '{zone}'. Explain your reasoning."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

# === Inventory Tools ===
@mcp.tool()
async def reorder_threshold(product: str, daily_usage: int, lead_time_days: int) -> dict:
    prompt = f"Determine the reorder threshold for {product} given a daily usage of {daily_usage} units and lead time of {lead_time_days} days. Please provide a step-by-step calculation."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def estimate_restock_time(product: str, current_stock: int, daily_usage: int) -> dict:
    prompt = f"Estimate how many days current stock of {current_stock} units for {product} will last, assuming a daily usage of {daily_usage}. Include your reasoning."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def suggest_inventory_kpis() -> dict:
    prompt = "List key performance indicators (KPIs) specifically for inventory management. Please explain how each KPI is relevant."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

# === Additional Tools to Reach 20 ===
@mcp.tool()
async def suggest_slotting_strategy(product_type: str) -> dict:
    prompt = f"Suggest a warehouse slotting strategy for {product_type} products. Provide reasoning for your recommendations."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def layout_optimization(warehouse_size: str) -> dict:
    prompt = f"Suggest layout optimization strategies for a {warehouse_size} warehouse. Please explain the rationale behind your suggestions."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def receiving_process_improvement() -> dict:
    prompt = "Suggest improvements for warehouse receiving and inbound logistics. Explain the reasoning behind your suggestions."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def warehouse_safety_checklist() -> dict:
    prompt = "Create a warehouse safety checklist for daily operations. Include reasoning for why each item is necessary."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def forecast_inventory(product: str, season: str) -> dict:
    prompt = f"Forecast inventory demand for {product} during the {season} season. Please explain the methodology you used to make the forecast."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def return_processing_guide() -> dict:
    prompt = "Provide best practices for processing returned goods in a warehouse. Explain why each practice is important."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def loading_dock_efficiency() -> dict:
    prompt = "Suggest ways to improve loading dock efficiency in logistics. Provide reasoning behind your suggestions."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def cycle_count_strategy() -> dict:
    prompt = "What is an effective cycle count strategy for inventory control? Please explain how it ensures accuracy."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def identify_bottlenecks() -> dict:
    prompt = "How can I identify and resolve bottlenecks in warehouse operations? Provide a step-by-step breakdown."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def fleet_optimization() -> dict:
    prompt = "Suggest fleet optimization strategies for a logistics company. Include reasoning for each suggestion."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def packaging_material_advice(product: str) -> dict:
    prompt = f"Suggest optimal packaging material for shipping {product}. Please explain the factors that influence your choice."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

@mcp.tool()
async def employee_training_plan(role: str) -> dict:
    prompt = f"Create a training plan for a new warehouse {role}. Provide reasoning behind the key components of the plan."
    result = await call_llm(prompt)
    return {"content": [TextContent(type="text", text=result)]}

if __name__ == "__main__":
    mcp.run(transport="stdio")
