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
    check_in_id = f"CHK-IN-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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
    check_out_id = f"CHK-OUT-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    result = {
        "success": True,
        "action": "check_out",
        "user_id": user_id,
        "timestamp": timestamp,
        "check_out_id": check_out_id,
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
    # Simulated balance retrieval
    return {
        "success": True,
        "user_id": user_id,
        "balances": {
            "pto": {
                "available": 12.5,
                "used": 2.5,
                "total": 15.0
            },
            "sick": {
                "available": 8.0,
                "used": 2.0,
                "total": 10.0
            },
            "unpaid": {
                "available": "unlimited",
                "used": 0,
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
    request_id = f"LR-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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
    # Simulated leave requests
    all_requests = [
        {
            "request_id": f"LR-{user_id}-20231101120000",
            "start_date": "2023-12-20",
            "end_date": "2023-12-27",
            "leave_type": "pto",
            "status": "approved",
            "reason": "Holiday vacation"
        },
        {
            "request_id": f"LR-{user_id}-20231115140000",
            "start_date": "2024-01-15",
            "end_date": "2024-01-15",
            "leave_type": "sick",
            "status": "pending",
            "reason": "Doctor appointment"
        }
    ]
    
    if filter_status != "all":
        filtered = [req for req in all_requests if req["status"] == filter_status]
    else:
        filtered = all_requests
    
    return {
        "success": True,
        "user_id": user_id,
        "filter_status": filter_status,
        "count": len(filtered),
        "requests": filtered
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
    correction_id = f"AC-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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
    ticket_id = f"HR-ESC-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
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


class HRAssist:
    """
    Main HR-Assist agent class.
    
    This class manages the conversation flow, enforces authentication,
    and coordinates tool usage according to the strict requirements.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, company_name: str = "CompanyName"):
        """
        Initialize the HR-Assist agent.
        
        Args:
            openai_api_key: OpenAI API key (defaults to env variable)
            company_name: Name of the company
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.company_name = company_name
        self.conversation_history = []
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        if OpenAI is None:
            raise ImportError("OpenAI package is required. Install with: pip install openai")
        
        self.client = OpenAI(api_key=self.api_key)
        
        self.system_prompt = f"""You are HR-Assist, a secure and empathetic HR operations assistant for {self.company_name}.

CRITICAL RULES YOU MUST FOLLOW:

1. AUTHENTICATION REQUIREMENT:
   - You MUST receive authenticated_user_id with every request
   - If authenticated_user_id is missing, REFUSE to operate and ask for it
   - Never proceed with any action without authenticated_user_id

2. POLICY INFORMATION:
   - For ALL questions about HR policies, benefits, procedures, or rules, you MUST use the search_hr_knowledge_base tool
   - NEVER guess or make up policy information
   - Only provide information retrieved from search_hr_knowledge_base
   - If search returns no results, say you can't find a specific policy and offer to escalate to human HR

3. ACTION TOOLS:
   - Always pass authenticated_user_id as user_id when calling action tools
   - Before calling any tool, ensure you have ALL required parameters
   - If parameters are missing, ask the user for them
   - After each tool call, provide a clear confirmation message with IDs and status

4. TONE:
   - Be professional, concise, and friendly
   - Show empathy and understanding
   - Never make jokes about serious HR matters
   - Be respectful of privacy and confidentiality

5. ESCALATION:
   - If you cannot help or find relevant policy information, offer to escalate to human HR
   - Use escalate_to_human_hr tool when appropriate

Remember: You are a helpful assistant, but you must strictly follow these rules for security and compliance."""
    
    def validate_authentication(self, authenticated_user_id: Optional[str]) -> bool:
        """
        Validate that authenticated_user_id is provided.
        
        Args:
            authenticated_user_id: The authenticated user ID from the request
            
        Returns:
            True if valid, False otherwise
        """
        return authenticated_user_id is not None and authenticated_user_id.strip() != ""
    
    def chat(
        self,
        user_message: str,
        authenticated_user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        Process a user message and return the assistant's response.
        
        Args:
            user_message: The user's message
            authenticated_user_id: Required authenticated user ID
            user_name: Optional user name for personalization
            
        Returns:
            The assistant's response as a string
        """
        # Validate authentication
        if not self.validate_authentication(authenticated_user_id):
            return (
                "❌ Authentication required. I cannot assist without your authenticated user ID. "
                "Please provide your authenticated_user_id to continue."
            )
        
        # Add user context to the message
        context_prefix = f"[Authenticated User: {authenticated_user_id}"
        if user_name:
            context_prefix += f", Name: {user_name}"
        context_prefix += "] "
        
        contextual_message = context_prefix + user_message
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": contextual_message
        })
        
        # Initial API call
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            # Process the response
            return self._process_response(response, authenticated_user_id)
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try again or contact support."
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            return error_msg
    
    def _process_response(self, response, authenticated_user_id: str) -> str:
        """
        Process the API response, handling tool calls if needed.
        
        Args:
            response: The API response object
            authenticated_user_id: The authenticated user ID
            
        Returns:
            The final assistant response as a string
        """
        assistant_message = response.choices[0].message
        
        # Check if there are tool calls
        if assistant_message.tool_calls:
            # Add assistant's message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Execute tool calls
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the function
                if function_name in TOOL_FUNCTIONS:
                    function_response = TOOL_FUNCTIONS[function_name](**function_args)
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(function_response)
                    })
            
            # Get final response from the model
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            final_response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=messages
            )
            
            final_message = final_response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })
            
            return final_message
        else:
            # No tool calls, just return the content
            content = assistant_message.content or "I apologize, but I'm not sure how to respond. Could you please rephrase your question?"
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            return content
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []


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
        agent = HRAssist(company_name=company_name)
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
            agent.reset_conversation()
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
