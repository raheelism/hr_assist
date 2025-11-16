"""
Verification script to check that HR-Assist meets all requirements.
"""

from hr_assist import (
    HRAssist,
    TOOLS,
    TOOL_FUNCTIONS,
    search_hr_knowledge_base,
    check_in,
    check_out,
    get_leave_balance,
    request_leave,
    get_leave_requests,
    correct_attendance,
    escalate_to_human_hr
)

def verify_requirements():
    """Verify that all requirements from the problem statement are met."""
    
    print("=" * 80)
    print("HR-ASSIST REQUIREMENTS VERIFICATION")
    print("=" * 80)
    print()
    
    results = []
    
    # Requirement 1: Authentication requirement
    print("✓ Requirement 1: Authentication Enforcement")
    print("  - HRAssist.validate_authentication() method implemented")
    print("  - chat() method checks authenticated_user_id")
    
    agent = HRAssist(openai_api_key="test-key")
    
    # Test without auth
    response = agent.chat("Hello", authenticated_user_id=None)
    assert "Authentication required" in response
    print("  ✓ Refuses to operate without authenticated_user_id")
    
    # Test with empty auth
    response = agent.chat("Hello", authenticated_user_id="")
    assert "Authentication required" in response
    print("  ✓ Refuses to operate with empty authenticated_user_id")
    
    results.append(("Authentication Enforcement", True))
    print()
    
    # Requirement 2: RAG tool for HR knowledge
    print("✓ Requirement 2: RAG-based Knowledge Search")
    print("  - search_hr_knowledge_base tool defined")
    
    tool_names = [tool["function"]["name"] for tool in TOOLS]
    assert "search_hr_knowledge_base" in tool_names
    print("  ✓ search_hr_knowledge_base tool exists in TOOLS")
    
    # Test search function
    result = search_hr_knowledge_base("PTO policy")
    assert result["found"] is True
    print("  ✓ search_hr_knowledge_base returns results for valid queries")
    
    result = search_hr_knowledge_base("nonexistent policy xyz")
    assert result["found"] is False
    print("  ✓ search_hr_knowledge_base returns 'not found' for invalid queries")
    
    results.append(("RAG Knowledge Search", True))
    print()
    
    # Requirement 3: Action tools with user_id parameter
    print("✓ Requirement 3: Action Tools")
    
    required_tools = [
        "check_in",
        "check_out",
        "get_leave_balance",
        "request_leave",
        "get_leave_requests",
        "correct_attendance",
        "escalate_to_human_hr"
    ]
    
    for tool_name in required_tools:
        assert tool_name in tool_names
        print(f"  ✓ {tool_name} tool exists")
    
    # Verify all action tools require user_id
    action_tools_check = [
        "check_in",
        "check_out",
        "get_leave_balance",
        "request_leave",
        "get_leave_requests",
        "correct_attendance",
        "escalate_to_human_hr"
    ]
    
    for tool_name in action_tools_check:
        tool = next(t for t in TOOLS if t["function"]["name"] == tool_name)
        required_params = tool["function"]["parameters"]["required"]
        assert "user_id" in required_params
        print(f"  ✓ {tool_name} requires user_id parameter")
    
    results.append(("Action Tools Implementation", True))
    print()
    
    # Requirement 4: Tool functions work correctly
    print("✓ Requirement 4: Tool Function Correctness")
    
    # Test check_in
    result = check_in("EMP-123")
    assert result["success"] is True
    assert result["user_id"] == "EMP-123"
    print("  ✓ check_in works correctly")
    
    # Test check_out
    result = check_out("EMP-123", note="End of day")
    assert result["success"] is True
    assert "note" in result
    print("  ✓ check_out works correctly")
    
    # Test get_leave_balance
    result = get_leave_balance("EMP-123")
    assert result["success"] is True
    assert "balances" in result
    print("  ✓ get_leave_balance works correctly")
    
    # Test request_leave
    result = request_leave("EMP-123", "2025-12-20", "2025-12-27", "pto", "Vacation")
    assert result["success"] is True
    assert result["status"] == "pending"
    print("  ✓ request_leave works correctly")
    
    # Test get_leave_requests
    result = get_leave_requests("EMP-123", "all")
    assert result["success"] is True
    assert "requests" in result
    print("  ✓ get_leave_requests works correctly")
    
    # Test correct_attendance
    result = correct_attendance("EMP-123", "2025-11-10", "wfh", "Forgot to log")
    assert result["success"] is True
    print("  ✓ correct_attendance works correctly")
    
    # Test escalate_to_human_hr
    result = escalate_to_human_hr("EMP-123", "Issue", "Summary")
    assert result["success"] is True
    assert result["status"] == "escalated"
    print("  ✓ escalate_to_human_hr works correctly")
    
    results.append(("Tool Functions", True))
    print()
    
    # Requirement 5: Proper parameter validation
    print("✓ Requirement 5: Parameter Validation")
    
    # Check request_leave has all required params
    tool = next(t for t in TOOLS if t["function"]["name"] == "request_leave")
    required = tool["function"]["parameters"]["required"]
    assert "user_id" in required
    assert "start_date" in required
    assert "end_date" in required
    assert "leave_type" in required
    assert "reason" in required
    print("  ✓ request_leave has all required parameters")
    
    # Check leave_type enum
    leave_type_enum = tool["function"]["parameters"]["properties"]["leave_type"]["enum"]
    assert set(leave_type_enum) == {"pto", "sick", "unpaid"}
    print("  ✓ leave_type has correct enum values: pto, sick, unpaid")
    
    # Check correct_attendance status enum
    tool = next(t for t in TOOLS if t["function"]["name"] == "correct_attendance")
    status_enum = tool["function"]["parameters"]["properties"]["status"]["enum"]
    assert set(status_enum) == {"present", "absent", "wfh", "half_day"}
    print("  ✓ attendance status has correct enum values: present, absent, wfh, half_day")
    
    results.append(("Parameter Validation", True))
    print()
    
    # Requirement 6: Proper system prompt
    print("✓ Requirement 6: System Prompt Configuration")
    
    agent = HRAssist(openai_api_key="test-key", company_name="TestCorp")
    
    assert "TestCorp" in agent.system_prompt
    print("  ✓ System prompt includes company name")
    
    assert "authenticated_user_id" in agent.system_prompt
    print("  ✓ System prompt mentions authentication requirement")
    
    assert "search_hr_knowledge_base" in agent.system_prompt
    print("  ✓ System prompt instructs to use RAG tool")
    
    assert "NEVER guess" in agent.system_prompt or "never make up" in agent.system_prompt.lower()
    print("  ✓ System prompt prohibits policy guessing/hallucination")
    
    assert "professional" in agent.system_prompt.lower() and "empathetic" in agent.system_prompt.lower()
    print("  ✓ System prompt defines proper tone")
    
    results.append(("System Prompt", True))
    print()
    
    # Requirement 7: Response handling
    print("✓ Requirement 7: Response Handling")
    
    # All tools return structured responses
    for func_name, func in TOOL_FUNCTIONS.items():
        if func_name == "search_hr_knowledge_base":
            result = func("test query")
        elif func_name in ["check_in", "get_leave_balance"]:
            result = func("EMP-123")
        elif func_name == "check_out":
            result = func("EMP-123", "note")
        elif func_name == "request_leave":
            result = func("EMP-123", "2025-12-20", "2025-12-27", "pto", "reason")
        elif func_name == "get_leave_requests":
            result = func("EMP-123", "all")
        elif func_name == "correct_attendance":
            result = func("EMP-123", "2025-11-10", "present", "reason")
        elif func_name == "escalate_to_human_hr":
            result = func("EMP-123", "topic", "summary")
        
        assert isinstance(result, dict)
        print(f"  ✓ {func_name} returns structured dict response")
    
    results.append(("Response Handling", True))
    print()
    
    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = all(result[1] for result in results)
    
    for requirement, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {requirement}")
    
    print()
    if all_passed:
        print("🎉 ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
    else:
        print("⚠️  Some requirements failed verification")
    
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = verify_requirements()
    exit(0 if success else 1)
