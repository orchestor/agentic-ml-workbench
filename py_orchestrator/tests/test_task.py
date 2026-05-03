from py_orchestrator.task import Task, TaskPriority, example_debug_recs_task


def test_example_debug_recs_task_has_expected_shape() -> None:
    task = example_debug_recs_task()

    assert task.id.startswith("debug-recs-ctr-drop")
    assert task.priority == TaskPriority.HIGH
    assert task.inputs["segment"] == "new_users_us"
    assert "root_cause_candidates" in task.done_definition.must_return_fields
    assert "suggested_experiments" in task.done_definition.must_return_fields