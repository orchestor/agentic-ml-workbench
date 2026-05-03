from dataclasses import dataclass

@dataclass
class Task:
    id: str
    intent: str

def echo_intent(task: Task) -> str:
    """
    minimum example: return the intent field of the task.
    we will upgrade it to a real orchestrator later.
    """
    return task.intent