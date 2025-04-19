# perception.py
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
from google import genai
from config import llm



class PerceptionInput(BaseModel):
    system_prompt: str
    user_query: str

class PerceptionOutput(BaseModel):
    llm_prompt: str
    model_response: str

def build_prompt(input_data: PerceptionInput) -> str:
    return f"{input_data.system_prompt}\n\nLogistics Query: {input_data.user_query}"

async def perceive(input_data: PerceptionInput) -> PerceptionOutput:
    # Load API key for Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(input_data)
    print("Sending prompt to Gemini...")
    response = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: client.models.generate_content(
            model=llm,
            contents=prompt
        )
    )
    return PerceptionOutput(llm_prompt=prompt, model_response=response.text.strip())