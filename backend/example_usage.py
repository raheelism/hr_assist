"""
Example usage of HR-Assist.

This script demonstrates various use cases and how to integrate HR-Assist
into your application.
"""

import os
from dotenv import load_dotenv
from hr_assist import HRAssist

# Load environment variables
load_dotenv()


def example_without_authentication():
    """Example: Trying to use HR-Assist without authentication."""
    print("=" * 60)
    print("Example 1: Without Authentication")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    # This should refuse to operate
    response = agent.chat(
        user_message="What is the PTO policy?",
        authenticated_user_id=None
    )
    
    print(f"\nUser: What is the PTO policy?")
    print(f"HR-Assist: {response}\n")


def example_policy_question():
    """Example: Asking about HR policy."""
    print("=" * 60)
    print("Example 2: Policy Question")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    response = agent.chat(
        user_message="What is the PTO policy?",
        authenticated_user_id="EMP-12345",
        user_name="John Doe"
    )
    
    print(f"\nUser (EMP-12345): What is the PTO policy?")
    print(f"HR-Assist: {response}\n")


def example_check_leave_balance():
    """Example: Checking leave balance."""
    print("=" * 60)
    print("Example 3: Check Leave Balance")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    response = agent.chat(
        user_message="Can you show me my leave balance?",
        authenticated_user_id="EMP-12345",
        user_name="John Doe"
    )
    
    print(f"\nUser (EMP-12345): Can you show me my leave balance?")
    print(f"HR-Assist: {response}\n")


def example_request_leave():
    """Example: Requesting leave."""
    print("=" * 60)
    print("Example 4: Request Leave")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    # Initial request (missing details)
    response1 = agent.chat(
        user_message="I need to take some time off next month",
        authenticated_user_id="EMP-12345",
        user_name="John Doe"
    )
    
    print(f"\nUser (EMP-12345): I need to take some time off next month")
    print(f"HR-Assist: {response1}\n")
    
    # Provide details
    response2 = agent.chat(
        user_message="I need PTO from December 20 to December 27 for holiday vacation",
        authenticated_user_id="EMP-12345",
        user_name="John Doe"
    )
    
    print(f"User (EMP-12345): I need PTO from December 20 to December 27 for holiday vacation")
    print(f"HR-Assist: {response2}\n")


def example_check_in():
    """Example: Checking in."""
    print("=" * 60)
    print("Example 5: Check-In")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    response = agent.chat(
        user_message="I need to check in for today",
        authenticated_user_id="EMP-12345",
        user_name="John Doe"
    )
    
    print(f"\nUser (EMP-12345): I need to check in for today")
    print(f"HR-Assist: {response}\n")


def example_multiple_questions():
    """Example: Multiple questions in same conversation."""
    print("=" * 60)
    print("Example 6: Multiple Questions in Same Conversation")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    # Question 1
    response1 = agent.chat(
        user_message="What are the benefits available to employees?",
        authenticated_user_id="EMP-12345",
        user_name="Jane Smith"
    )
    
    print(f"\nUser (EMP-12345): What are the benefits available to employees?")
    print(f"HR-Assist: {response1}\n")
    
    # Question 2 (context maintained)
    response2 = agent.chat(
        user_message="Can you also check my leave balance?",
        authenticated_user_id="EMP-12345",
        user_name="Jane Smith"
    )
    
    print(f"User (EMP-12345): Can you also check my leave balance?")
    print(f"HR-Assist: {response2}\n")


def example_escalation():
    """Example: Escalating to human HR."""
    print("=" * 60)
    print("Example 7: Escalation to Human HR")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    # Ask about something not in knowledge base
    response1 = agent.chat(
        user_message="What is the policy for stock options?",
        authenticated_user_id="EMP-12345",
        user_name="Alex Johnson"
    )
    
    print(f"\nUser (EMP-12345): What is the policy for stock options?")
    print(f"HR-Assist: {response1}\n")
    
    # Request human assistance
    response2 = agent.chat(
        user_message="Yes, please connect me with someone from HR",
        authenticated_user_id="EMP-12345",
        user_name="Alex Johnson"
    )
    
    print(f"User (EMP-12345): Yes, please connect me with someone from HR")
    print(f"HR-Assist: {response2}\n")


def example_attendance_correction():
    """Example: Correcting attendance."""
    print("=" * 60)
    print("Example 8: Attendance Correction")
    print("=" * 60)
    
    agent = HRAssist(company_name="CompanyName")
    
    response = agent.chat(
        user_message="I need to correct my attendance for November 10th. I worked from home but it shows absent.",
        authenticated_user_id="EMP-12345",
        user_name="Sarah Williams"
    )
    
    print(f"\nUser (EMP-12345): I need to correct my attendance for November 10th. I worked from home but it shows absent.")
    print(f"HR-Assist: {response}\n")


def run_all_examples():
    """Run all examples."""
    examples = [
        example_without_authentication,
        example_policy_question,
        example_check_leave_balance,
        example_request_leave,
        example_check_in,
        example_multiple_questions,
        example_escalation,
        example_attendance_correction
    ]
    
    for example in examples:
        try:
            example()
            input("Press Enter to continue to next example...")
            print("\n\n")
        except KeyboardInterrupt:
            print("\n\nExiting examples...")
            break
        except Exception as e:
            print(f"\nError in example: {e}")
            print("Make sure you have set OPENAI_API_KEY in your .env file\n")
            input("Press Enter to continue to next example...")


if __name__ == "__main__":
    print("\n")
    print("🤖 HR-Assist Example Usage")
    print("=" * 60)
    print("These examples demonstrate various use cases of HR-Assist")
    print("=" * 60)
    print("\n")
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set!")
        print("Please set OPENAI_API_KEY in your .env file to run the examples.")
        print("\nYou can still see the structure, but API calls will fail.\n")
    
    try:
        run_all_examples()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
