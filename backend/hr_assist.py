"""
HR-Assist: A production-ready HR operations assistant bot.

This module implements a secure, empathetic HR assistant that handles employee
inquiries about policies, benefits, and HR operations while maintaining strict
authentication and using RAG for knowledge retrieval.
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from database import get_db_path
import sqlite3

# Tool function implementations (simulated backend calls)
# In production, these would connect to actual HR systems

def search_hr_knowledge_base(query: str) -> Dict[str, Any]:
    """
    Search the HR knowledge base using RAG.
    
    Args:
        query: The search query from the user
        
    Returns:
        Dictionary with search results and relevant policy information
    """
    # This is a simulated RAG search. In production, this would connect to
    # a vector database or knowledge base with actual HR policies.
    
    # Simulated knowledge base responses
    knowledge_base = {
        "pto": {
            "content": "PTO (Paid Time Off) Policy: Employees receive 15 days of PTO annually. "
                      "PTO accrues monthly at 1.25 days per month. Requests should be submitted "
                      "at least 2 weeks in advance. Maximum carryover is 5 days to next year.",
            "relevance": 0.95
        },
        "sick": {
            "content": "Sick Leave Policy: Employees receive 10 days of sick leave annually. "
                      "Sick leave can be taken without prior notice but requires notification "
                      "within 2 hours of shift start. Doctor's note required for 3+ consecutive days.",
            "relevance": 0.92
        },
        "benefits": {
            "content": "Benefits Package: Comprehensive health insurance (medical, dental, vision), "
                      "401(k) with 4% company match, life insurance, disability insurance, "
                      "and wellness programs. Enrollment period is in November each year.",
            "relevance": 0.88
        },
        "remote work": {
            "content": "Remote Work Policy: Employees may work remotely up to 2 days per week "
                      "with manager approval. Full-time remote arrangements require VP approval. "
                      "Equipment stipend of $500 annually for home office setup.",
            "relevance": 0.90
        },
        "attendance": {
            "content": "Attendance Policy: Employees must check in/out daily. Core hours are 9 AM - 5 PM. "
                      "Flexible scheduling available with manager approval. Unauthorized absences "
                      "may result in disciplinary action.",
            "relevance": 0.87
        }
    }
    
    query_lower = query.lower()
    results = []
    
    for topic, data in knowledge_base.items():
        if topic in query_lower or any(word in query_lower for word in topic.split()):
            results.append({
                "content": data["content"],
                "relevance": data["relevance"],
                "topic": topic
            })
    
    if results:
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return {
            "found": True,
            "results": results,
            "query": query
        }
    else:
        return {
            "found": False,
            "results": [],
            "query": query
        }

def check_in(user_id: str) -> Dict[str, Any]:
    """
    Record employee check-in.
    
    Args:
        user_id: Authenticated user ID
        
    Returns:
        Confirmation with timestamp and check-in ID
    """
    timestamp = datetime.now().isoformat()
    date = datetime.now().strftime('%Y-%m-%d')

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO attendance (employee_id, check_in, date) VALUES (?, ?, ?)", (user_id, timestamp, date))
    check_in_id = cursor.lastrowid

    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "action": "check_in",
        "user_id": user_id,
        "timestamp": timestamp,
        "check_in_id": check_in_id,
        "message": f"Successfully checked in at {timestamp}"
    }

def check_out(user_id: str, note: Optional[str] = None) -> Dict[str, Any]:
    """
    Record employee check-out.
    
    Args:
        user_id: Authenticated user ID
        note: Optional note for the check-out
        
    Returns:
        Confirmation with timestamp and check-out ID
    """
    timestamp = datetime.now().isoformat()
    date = datetime.now().strftime('%Y-%m-%d')

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("UPDATE attendance SET check_out = ? WHERE employee_id = ? AND date = ?", (timestamp, user_id, date))

    conn.commit()
    conn.close()
    
    result = {
        "success": True,
        "action": "check_out",
        "user_id": user_id,
        "timestamp": timestamp,
        "message": f"Successfully checked out at {timestamp}"
    }
    
    if note:
        result["note"] = note
        result["message"] += f" with note: {note}"
    
    return result

def get_leave_balance(user_id: str) -> Dict[str, Any]:
    """
    Retrieve employee leave balance.
    
    Args:
        user_id: Authenticated user ID
        
    Returns:
        Current leave balances by type
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_pto = 15
    total_sick = 10

    cursor.execute("SELECT SUM(julianday(end_date) - julianday(start_date) + 1) FROM leaves WHERE employee_id = ? AND leave_type = 'pto' AND status = 'approved'", (user_id,))
    used_pto = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(julianday(end_date) - julianday(start_date) + 1) FROM leaves WHERE employee_id = ? AND leave_type = 'sick' AND status = 'approved'", (user_id,))
    used_sick = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(julianday(end_date) - julianday(start_date) + 1) FROM leaves WHERE employee_id = ? AND leave_type = 'unpaid' AND status = 'approved'", (user_id,))
    used_unpaid = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "success": True,
        "user_id": user_id,
        "balances": {
            "pto": {
                "available": total_pto - used_pto,
                "used": used_pto,
                "total": total_pto
            },
            "sick": {
                "available": total_sick - used_sick,
                "used": used_sick,
                "total": total_sick
            },
            "unpaid": {
                "available": "unlimited",
                "used": used_unpaid,
                "total": "unlimited"
            }
        },
        "as_of_date": datetime.now().strftime('%Y-%m-%d')
    }

def request_leave(
    user_id: str,
    start_date: str,
    end_date: str,
    leave_type: str,
    reason: str
) -> Dict[str, Any]:
    """
    Submit a leave request.
    
    Args:
        user_id: Authenticated user ID
        start_date: Leave start date (YYYY-MM-DD)
        end_date: Leave end date (YYYY-MM-DD)
        leave_type: Type of leave (pto, sick, unpaid)
        reason: Reason for leave
        
    Returns:
        Confirmation with request ID and status
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO leaves (employee_id, start_date, end_date, leave_type, reason, status) VALUES (?, ?, ?, ?, ?, ?)", (user_id, start_date, end_date, leave_type, reason, "pending"))
    request_id = cursor.lastrowid

    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "action": "request_leave",
        "request_id": request_id,
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "leave_type": leave_type,
        "reason": reason,
        "status": "pending",
        "message": f"Leave request {request_id} submitted successfully. Status: pending approval."
    }

def get_leave_requests(
    user_id: str,
    filter_status: Optional[str] = "all"
) -> Dict[str, Any]:
    """
    Retrieve employee leave requests.
    
    Args:
        user_id: Authenticated user ID
        filter_status: Filter by status (pending, approved, all)
        
    Returns:
        List of leave requests matching the filter
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if filter_status == "all":
        cursor.execute("SELECT id, start_date, end_date, leave_type, status, reason FROM leaves WHERE employee_id = ?", (user_id,))
    else:
        cursor.execute("SELECT id, start_date, end_date, leave_type, status, reason FROM leaves WHERE employee_id = ? AND status = ?", (user_id, filter_status))

    requests = []
    for row in cursor.fetchall():
        requests.append({
            "request_id": row[0],
            "start_date": row[1],
            "end_date": row[2],
            "leave_type": row[3],
            "status": row[4],
            "reason": row[5]
        })

    conn.close()
    
    return {
        "success": True,
        "user_id": user_id,
        "filter_status": filter_status,
        "count": len(requests),
        "requests": requests
    }

def correct_attendance(
    user_id: str,
    date: str,
    status: str,
    reason: str
) -> Dict[str, Any]:
    """
    Submit an attendance correction request.
    
    Args:
        user_id: Authenticated user ID
        date: Date to correct (YYYY-MM-DD)
        status: Attendance status (present, absent, wfh, half_day)
        reason: Reason for correction
        
    Returns:
        Confirmation with correction ID
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM attendance WHERE employee_id = ? AND date = ?", (user_id, date))
    record = cursor.fetchone()

    if record:
        cursor.execute("UPDATE attendance SET check_in = ?, check_out = ? WHERE id = ?", (status, f"Corrected: {reason}", record[0]))
    else:
        cursor.execute("INSERT INTO attendance (employee_id, date, check_in, check_out) VALUES (?, ?, ?, ?)", (user_id, date, status, f"Corrected: {reason}"))

    correction_id = cursor.lastrowid or record[0]

    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "action": "correct_attendance",
        "correction_id": correction_id,
        "user_id": user_id,
        "date": date,
        "status": status,
        "reason": reason,
        "message": f"Attendance correction {correction_id} submitted for {date}. "
                  f"Status changed to: {status}. Pending approval."
    }

def escalate_to_human_hr(
    user_id: str,
    topic: str,
    chat_history_summary: str
) -> Dict[str, Any]:
    """
    Escalate the conversation to a human HR representative.
    
    Args:
        user_id: Authenticated user ID
        topic: Short description of the topic
        chat_history_summary: Brief summary of the conversation
        
    Returns:
        Confirmation with escalation ticket ID
    """
    timestamp = datetime.now().isoformat()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    details = f"Topic: {topic}, Summary: {chat_history_summary}"
    cursor.execute("INSERT INTO audit_log (timestamp, user_id, action, details) VALUES (?, ?, ?, ?)", (timestamp, user_id, "escalation", details))
    ticket_id = cursor.lastrowid

    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "action": "escalate_to_human_hr",
        "ticket_id": ticket_id,
        "user_id": user_id,
        "topic": topic,
        "status": "escalated",
        "message": f"Your request has been escalated to human HR. "
                  f"Ticket ID: {ticket_id}. An HR representative will contact you within 24 hours."
    }

# Tool definitions for the agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_hr_knowledge_base",
            "description": "Search the HR knowledge base for policies, benefits, procedures, and rules. "
                          "Always use this tool to answer questions about HR policies. "
                          "Never guess or make up policy information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question or search query about HR policies, benefits, or procedures"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_in",
            "description": "Record an employee check-in for attendance tracking. "
                          "Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_out",
            "description": "Record an employee check-out for attendance tracking. "
                          "Requires authenticated user_id. Accepts optional note.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note for the check-out"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_balance",
            "description": "Retrieve the employee's current leave balance including PTO, sick leave, and unpaid leave. "
                          "Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_leave",
            "description": "Submit a new leave request. Must collect all required parameters from the user. "
                          "Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Leave start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Leave end date in YYYY-MM-DD format"
                    },
                    "leave_type": {
                        "type": "string",
                        "enum": ["pto", "sick", "unpaid"],
                        "description": "Type of leave: pto (paid time off), sick, or unpaid"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the leave request"
                    }
                },
                "required": ["user_id", "start_date", "end_date", "leave_type", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_requests",
            "description": "Retrieve the employee's leave request history. "
                          "Can filter by status. Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    },
                    "filter_status": {
                        "type": "string",
                        "enum": ["pending", "approved", "all"],
                        "description": "Filter leave requests by status: pending, approved, or all"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "correct_attendance",
            "description": "Submit a request to correct attendance records for a specific date. "
                          "Must collect all required parameters from the user. Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date to correct in YYYY-MM-DD format"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["present", "absent", "wfh", "half_day"],
                        "description": "Correct attendance status: present, absent, wfh (work from home), or half_day"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the attendance correction"
                    }
                },
                "required": ["user_id", "date", "status", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human_hr",
            "description": "Escalate the conversation to a human HR representative when unable to help "
                          "or when the user requests human assistance. Requires authenticated user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The authenticated user ID from the request"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Short description of the topic or issue"
                    },
                    "chat_history_summary": {
                        "type": "string",
                        "description": "Brief summary of the conversation so far"
                    }
                },
                "required": ["user_id", "topic", "chat_history_summary"]
            }
        }
    }
]

# Map function names to actual implementations
TOOL_FUNCTIONS = {
    "search_hr_knowledge_base": search_hr_knowledge_base,
    "check_in": check_in,
    "check_out": check_out,
    "get_leave_balance": get_leave_balance,
    "request_leave": request_leave,
    "get_leave_requests": get_leave_requests,
    "correct_attendance": correct_attendance,
    "escalate_to_human_hr": escalate_to_human_hr
}

def main():
    """
    Main function to demonstrate HR-Assist usage.
    """
    import sys
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    company_name = os.getenv("COMPANY_NAME", "CompanyName")
    
    print(f"🤖 HR-Assist for {company_name}")
    print("=" * 60)
    print("Welcome! I'm your HR assistant.")
    print("Type 'quit' to exit, 'reset' to start a new conversation")
    print("=" * 60)
    print()
    
    # Initialize the agent
    try:
        from agent import HRAssistAgent
        agent = HRAssistAgent()
    except Exception as e:
        print(f"Error initializing HR-Assist: {e}")
        sys.exit(1)
    
    # Get user authentication (in production, this would come from your auth system)
    authenticated_user_id = input("Please enter your user ID: ").strip()
    user_name = input("Please enter your name (optional): ").strip() or None
    
    print()
    print("Authentication successful! How can I help you today?")
    print()
    
    # Chat loop
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Thank you for using HR-Assist. Have a great day!")
            break
        
        if user_input.lower() == 'reset':
            # This is a bit of a hack to reset the agent's state
            agent = HRAssistAgent()
            print("Conversation reset. Starting fresh!")
            continue
        
        # Get response from agent
        response = agent.chat(
            user_message=user_input,
            authenticated_user_id=authenticated_user_id,
            user_name=user_name
        )
        
        print(f"\nHR-Assist: {response}\n")

if __name__ == "__main__":
    main()
