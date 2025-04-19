# memory.py
from pydantic import BaseModel
from typing import Dict

class MemoryInput(BaseModel):
    key: str
    value: dict

class MemoryOutput(BaseModel):
    memory_store: Dict[str, dict]

memory_db = {}

def store_memory(mem_input: MemoryInput) -> MemoryOutput:
    memory_db[mem_input.key] = mem_input.value
    return MemoryOutput(memory_store=memory_db)

def get_memory(key: str) -> dict:
    return memory_db.get(key, {})