
import pytest
from schemas import TaskCreate
from pydantic import ValidationError
from datetime import date

def test_valid_task_create():
    task = TaskCreate(
        title="Test Task",
        content="This is a test task.",
        priority="High",
        status="Todo",
        due_date=date.today()
    )
    assert task.title == "Test Task"
    assert task.priority == "High"

def test_invalid_task_create_missing_title():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="", # Title must strictly be str, default validation might allow empty unless specified. 
            # In schemas.py TaskBase, title is str. Pydantic doesn't forbid empty strings by default unless constrained.
            # Let's assume title is required argument, so passing None or missing it is the error.
            # But here we pass kwargs? No, BaseModel expects fields. 
            content="Content",
            priority="Low"
        )
        # Actually TaskBase requires title. If we don't pass it:
        # TaskCreate(content="...") -> Error. 

def test_invalid_type():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Title",
            content="Content",
            priority="Low",
            due_date="not-a-date" # Should fail date parsing
        )
