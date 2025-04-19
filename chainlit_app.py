# chainlit_app.py

import chainlit as cl
import os
from agent import main

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="🔐 Welcome to the Warehouse Automation Agent! Let's gather some configuration.").send()

    # Ask user for all configuration values
    api_key_msg = await cl.AskUserMessage(content="Enter your GEMINI API Key:").send()
    warehouse_msg = await cl.AskUserMessage(content="Enter warehouse location:").send()
    shipment_msg = await cl.AskUserMessage(content="Enter daily shipment volume:").send()
    automation_msg = await cl.AskUserMessage(content="Automation level (low, medium, high):").send()


    # Store API key in env var for downstream use
    if os.getenv("GEMINI_API_KEY") is None:
        os.environ["GEMINI_API_KEY"] = api_key_msg["output"]

    # Store user settings in session
    cl.user_session.set("warehouse_location", warehouse_msg['output'])
    cl.user_session.set("shipment_volume", shipment_msg['output'])
    cl.user_session.set("automation_level", automation_msg['output'])

    await cl.Message(content="✅ Setup complete! Now send your logistics query.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Get setup values
    warehouse_location = cl.user_session.get("warehouse_location")
    shipment_volume = cl.user_session.get("shipment_volume")
    automation_level = cl.user_session.get("automation_level")

    # Run agent
    await main(
        warehouse_location=warehouse_location,
        shipment_volume=shipment_volume,
        automation_level=automation_level,
        initial_query=message.content,
    )
