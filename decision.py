# decision.py
from pydantic import BaseModel
from typing import Any

class DecisionInput(BaseModel):
    model_response: str

class DecisionOutput(BaseModel):
    action_type: str
    tool_name: str
    arguments: dict

def make_decision(dec_input: DecisionInput) -> DecisionOutput:
    text = dec_input.model_response.strip()
    text = text.replace("```json", "").replace("```", "").replace("\\n", "").strip()
    if text.startswith("FUNCTION_CALL:"):
        import json
        content = text.split("FUNCTION_CALL:", 1)[-1].strip()
        data = json.loads(content)
        return DecisionOutput(action_type="function_call", tool_name=data['name'], arguments=data['arguments'])
    elif text.startswith("FINAL_ANSWER:"):
        return DecisionOutput(action_type="final_answer", tool_name="", arguments={"answer": text.split(":",1)[-1].strip()})
    elif text.startswith("COMPLETE_RUN"):
        return DecisionOutput(action_type="complete_run", tool_name="", arguments={})
    else:
        return DecisionOutput(action_type="unknown", tool_name="", arguments={})