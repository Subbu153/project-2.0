
import pytest
from unittest.mock import MagicMock
from app import create_task, delete_task
from models import Task
from datetime import date

def test_create_task_success():
    # Mock Session
    mock_db = MagicMock()
    
    # Call function
    task, error = create_task(
        db=mock_db,
        title="New Task",
        content="Content here",
        priority="High",
        status="Todo",
        due_date=date.today()
    )
    
    # Verify interactions
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert task is not None
    assert error is None
    assert task.title == "New Task"

def test_delete_task_success():
    mock_db = MagicMock()
    
    # Mock query return
    mock_task = Task(id=1, title="Delete Me")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_task
    
    success, error = delete_task(mock_db, 1)
    
    assert mock_db.delete.called_with(mock_task)
    assert mock_db.commit.called
    assert success is True
    assert error[0] == 200

def test_delete_task_not_found():
    mock_db = MagicMock()
    # Mock query return None
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    success, error = delete_task(mock_db, 999)
    
    assert not mock_db.delete.called
    assert success is False
    assert error[0] == 404
