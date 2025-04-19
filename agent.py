# main.py
import asyncio
import chainlit as cl
from perception import perceive, PerceptionInput
from memory import store_memory, MemoryInput, get_memory
from decision import make_decision, DecisionInput
from action import take_action, ActionInput

# Add this to the top or import from another file
def verify_action_type_from_llm(response: str) -> str:
    response_lower = response.lower()
    if "task finished" in response_lower or "logistics task finished" in response_lower:
        return "complete_run"
    elif "answer" in response_lower or "summary" in response_lower or "recommendation" in response_lower:
        return "final_answer"
    return "unknown"


def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main(warehouse_location,shipment_volume,automation_level,initial_query):
    print("Welcome to the Logistics and Warehouse Cognitive Agent! Let's collect your preferences first.")
    try:
        preferences = {
            "warehouse_location": warehouse_location,
            "shipment_volume": shipment_volume,
            "automation_level": automation_level
        }

        store_memory(MemoryInput(key="user_preferences", value=preferences))
        memory_data = get_memory("user_preferences")
        
        system_prompt = f"""You are a logistics and warehouse automation agent specialized in supply chain optimization, inventory control, and efficiency strategies.
        
        Warehouse: {memory_data.get("warehouse_location", "unknown")}  
        Daily Shipments: {memory_data.get("shipment_volume", "unknown")}  
        Automation: {memory_data.get("automation_level", "unknown")}  

                Respond using ONLY one of these formats:

                FUNCTION_CALL: {{
                "name": "<tool_name>",
                "arguments": {{
                    "param1": value1,
                    "param2": value2
                }}
                }}  
                FINAL_ANSWER: <string>  
                COMPLETE_RUN

                You can suggest KPIs, route improvements, layout strategies, or take actions using the following tools:

                Logistics & Operations:
                - suggest_kpis
                - calculate_storage_utilization(total_capacity: int, used_capacity: int)
                - optimize_picking_route(zone: str)
                - layout_optimization(warehouse_size: str)
                - receiving_process_improvement()
                - warehouse_safety_checklist()
                - loading_dock_efficiency()
                - identify_bottlenecks()
                - fleet_optimization()

                Inventory Management:
                - suggest_inventory_kpis()
                - reorder_threshold(product: str, daily_usage: int, lead_time_days: int)
                - estimate_restock_time(product: str, current_stock: int, daily_usage: int)
                - cycle_count_strategy()
                - forecast_inventory(product: str, season: str)
                - return_processing_guide()

                Slotting & Packaging:
                - suggest_slotting_strategy(product_type: str)
                - packaging_material_advice(product: str)

                Training & Workforce:
                - employee_training_plan(role: str)

                Rules:
                - All FUNCTION_CALLs MUST be valid JSON. Each must return an object with "name" and "arguments".
                - If the response includes phrases like "need more information" or "cannot directly answer" or indicates missing input, respond with a new FUNCTION_CALL to request the required data using the tools listed.
                - Do not generate explanations, summaries, or conclusions outside the FINAL_ANSWER or COMPLETE_RUN format.
                - If a role like "forklift operator" or "warehouse manager" is mentioned, use employee_training_plan.

                Additional Instructions:
                - Self-Check: After selecting a tool or suggesting a strategy, verify that the input parameters are complete and reasonable. If not, respond with a FUNCTION_CALL to gather missing data.
                - Reasoning Type: For each FUNCTION_CALL, briefly annotate the type of reasoning involved using a comment inside the JSON. For example:
                FUNCTION_CALL: {{
                    "name": "reorder_threshold",
                    "arguments": {{
                    "product": "widget-A",
                    "daily_usage": 50,
                    "lead_time_days": 3
                    }}                    
                }}
                - If unsure or conflicted between tools, prefer the one with more direct impact on efficiency, and explain reasoning inside a comment block (inline with JSON if possible).

            """

        #initial_query = input("Please enter your logistics or warehouse query: ")
        current_query = initial_query
        #last_response = None
        max_iterations = 3
        iteration = 0

        while iteration < max_iterations:
            print(f"\n--- Iteration {iteration + 1} ---")

            # Step 1: Run perception
            perception_result = await perceive(PerceptionInput(system_prompt=system_prompt, user_query=current_query))

            print("\n--- Gemini Prompt Sent ---")
            print(perception_result.llm_prompt)
            print("\n--- Gemini Response ---")
            print(perception_result.model_response)

            # Step 2: Make decision
            decision = make_decision(DecisionInput(model_response=perception_result.model_response))

            # Step 3: Take action
            action = take_action(ActionInput(
                action_type=decision.action_type,
                tool_name=decision.tool_name,
                arguments=decision.arguments
            ))

            print("\nAgent Output:", action.result)

            # Step 4: Combine perception and action outputs
            combined_prompt = f"""
            You are a cognitive agent that first perceives input and then takes an action based on the perception.

            Here is what was perceived:
            {perception_result.model_response}

            Here is the action that was taken as a result:
            {action.result}

            Based on both the perception and the action result, synthesize a final answer that is helpful, complete, and user-facing. Do not repeat the steps. Provide a clear and final response.
            """
            # Step 5: Send combined prompt to LLM
            final_result = asyncio.run(perceive(PerceptionInput(system_prompt=system_prompt, user_query=combined_prompt)))

            print("\n--- Final LLM Prompt Sent ---")
            print(final_result.llm_prompt)
            print("\n--- Final LLM Response ---")
            print(final_result.model_response)

            # Use LLM-style verification to decide if we're done
            verified_type = verify_action_type_from_llm(final_result.model_response)

            if verified_type in ["final_answer", "complete_run"]:
                print(f"\n[Agent Determined Completion: {verified_type.upper()}]")
                await cl.Message(content=final_result.model_response).send() 
                break
                

            # Prepare for next iteration
            iteration += 1
            #last_response = final_result.model_response
            current_query += "\n\n" + final_result.model_response + "\nWhat should I do next?"

    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state()  # Reset at the end of main