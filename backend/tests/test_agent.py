import pytest
import os
import sqlite3
from unittest.mock import patch

# Add the backend directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db_path
from hr_assist import check_in, check_out, get_leave_balance, request_leave, get_leave_requests, correct_attendance

def test_check_in_and_out():
    # Test check-in
    check_in_result = check_in("EMP-123")
    assert check_in_result["success"] is True
    assert check_in_result["user_id"] == "EMP-123"

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT check_in, check_out FROM attendance WHERE employee_id = ?", ("EMP-123",))
    record = cursor.fetchone()
    assert record is not None
    assert record[0] is not None
    assert record[1] is None
    conn.close()

    # Test check-out
    check_out_result = check_out("EMP-123")
    assert check_out_result["success"] is True

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT check_in, check_out FROM attendance WHERE employee_id = ?", ("EMP-123",))
    record = cursor.fetchone()
    assert record is not None
    assert record[0] is not None
    assert record[1] is not None
    conn.close()

def test_leave_management():
    # Request a leave
    request_result = request_leave("EMP-123", "2025-12-20", "2025-12-22", "pto", "Vacation")
    assert request_result["success"] is True
    assert request_result["status"] == "pending"

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaves WHERE employee_id = ?", ("EMP-123",))
    assert cursor.fetchone() is not None
    conn.close()

    # Get leave requests
    requests_result = get_leave_requests("EMP-123")
    assert requests_result["success"] is True
    assert len(requests_result["requests"]) == 1
    assert requests_result["requests"][0]["status"] == "pending"

    # Approve the leave
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE leaves SET status = 'approved' WHERE employee_id = ?", ("EMP-123",))
    conn.commit()
    conn.close()

    # Check leave balance
    balance_result = get_leave_balance("EMP-123")
    assert balance_result["success"] is True
    assert balance_result["balances"]["pto"]["used"] == 3
    assert balance_result["balances"]["pto"]["available"] == 12

def test_correct_attendance():
    # Correct attendance for a date that doesn't exist
    correction_result = correct_attendance("EMP-123", "2025-11-10", "wfh", "Forgot to log")
    assert correction_result["success"] is True

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT check_in FROM attendance WHERE employee_id = ? AND date = ?", ("EMP-123", "2025-11-10"))
    assert cursor.fetchone()[0] == "wfh"
    conn.close()

    # Correct attendance for an existing date
    correction_result = correct_attendance("EMP-123", "2025-11-10", "present", "Came to office")
    assert correction_result["success"] is True

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT check_in FROM attendance WHERE employee_id = ? AND date = ?", ("EMP-123", "2025-11-10"))
    assert cursor.fetchone()[0] == "present"
    conn.close()
