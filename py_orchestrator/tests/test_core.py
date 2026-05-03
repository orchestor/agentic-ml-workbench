from py_orchestrator.core import Task, echo_intent

def test_echo_intent():
    task = Task(id="t1", intent="check-ci")
    assert echo_intent(task) == "check-ci"