"""
Tests for HR-Assist functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hr_assist import (
    HRAssist,
    search_hr_knowledge_base,
    check_in,
    check_out,
    get_leave_balance,
    request_leave,
    get_leave_requests,
    correct_attendance,
    escalate_to_human_hr,
    TOOLS,
    TOOL_FUNCTIONS
)


class TestToolFunctions:
    """Test the individual tool functions."""
    
    def test_search_hr_knowledge_base_found(self):
        """Test searching knowledge base with results."""
        result = search_hr_knowledge_base("PTO policy")
        
        assert result["found"] is True
        assert len(result["results"]) > 0
        assert "content" in result["results"][0]
        assert result["query"] == "PTO policy"
    
    def test_search_hr_knowledge_base_not_found(self):
        """Test searching knowledge base with no results."""
        result = search_hr_knowledge_base("completely unrelated topic xyz123")
        
        assert result["found"] is False
        assert len(result["results"]) == 0
    
    def test_check_in(self):
        """Test check-in function."""
        result = check_in("EMP-12345")
        
        assert result["success"] is True
        assert result["action"] == "check_in"
        assert result["user_id"] == "EMP-12345"
        assert "check_in_id" in result
        assert "timestamp" in result
    
    def test_check_out_without_note(self):
        """Test check-out without note."""
        result = check_out("EMP-12345")
        
        assert result["success"] is True
        assert result["action"] == "check_out"
        assert result["user_id"] == "EMP-12345"
        assert "check_out_id" in result
        assert "note" not in result
    
    def test_check_out_with_note(self):
        """Test check-out with note."""
        result = check_out("EMP-12345", note="Finished early")
        
        assert result["success"] is True
        assert result["note"] == "Finished early"
        assert "Finished early" in result["message"]
    
    def test_get_leave_balance(self):
        """Test getting leave balance."""
        result = get_leave_balance("EMP-12345")
        
        assert result["success"] is True
        assert result["user_id"] == "EMP-12345"
        assert "balances" in result
        assert "pto" in result["balances"]
        assert "sick" in result["balances"]
        assert "unpaid" in result["balances"]
    
    def test_request_leave(self):
        """Test requesting leave."""
        result = request_leave(
            user_id="EMP-12345",
            start_date="2025-12-20",
            end_date="2025-12-27",
            leave_type="pto",
            reason="Holiday vacation"
        )
        
        assert result["success"] is True
        assert result["action"] == "request_leave"
        assert result["user_id"] == "EMP-12345"
        assert result["start_date"] == "2025-12-20"
        assert result["end_date"] == "2025-12-27"
        assert result["leave_type"] == "pto"
        assert result["status"] == "pending"
        assert "request_id" in result
    
    def test_get_leave_requests_all(self):
        """Test getting all leave requests."""
        result = get_leave_requests("EMP-12345", filter_status="all")
        
        assert result["success"] is True
        assert result["user_id"] == "EMP-12345"
        assert result["filter_status"] == "all"
        assert "requests" in result
        assert result["count"] >= 0
    
    def test_get_leave_requests_pending(self):
        """Test getting pending leave requests."""
        result = get_leave_requests("EMP-12345", filter_status="pending")
        
        assert result["success"] is True
        assert result["filter_status"] == "pending"
        # All returned requests should be pending
        for req in result["requests"]:
            assert req["status"] == "pending"
    
    def test_correct_attendance(self):
        """Test correcting attendance."""
        result = correct_attendance(
            user_id="EMP-12345",
            date="2025-11-10",
            status="wfh",
            reason="Forgot to log WFH status"
        )
        
        assert result["success"] is True
        assert result["action"] == "correct_attendance"
        assert result["user_id"] == "EMP-12345"
        assert result["date"] == "2025-11-10"
        assert result["status"] == "wfh"
        assert "correction_id" in result
    
    def test_escalate_to_human_hr(self):
        """Test escalating to human HR."""
        result = escalate_to_human_hr(
            user_id="EMP-12345",
            topic="Compensation inquiry",
            chat_history_summary="User asked about salary adjustment"
        )
        
        assert result["success"] is True
        assert result["action"] == "escalate_to_human_hr"
        assert result["user_id"] == "EMP-12345"
        assert result["status"] == "escalated"
        assert "ticket_id" in result


class TestToolDefinitions:
    """Test that tool definitions are properly structured."""
    
    def test_all_tools_defined(self):
        """Test that all required tools are defined."""
        tool_names = [tool["function"]["name"] for tool in TOOLS]
        
        expected_tools = [
            "search_hr_knowledge_base",
            "check_in",
            "check_out",
            "get_leave_balance",
            "request_leave",
            "get_leave_requests",
            "correct_attendance",
            "escalate_to_human_hr"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    def test_tool_functions_mapped(self):
        """Test that all tool functions are properly mapped."""
        for tool in TOOLS:
            function_name = tool["function"]["name"]
            assert function_name in TOOL_FUNCTIONS
            assert callable(TOOL_FUNCTIONS[function_name])
    
    def test_tools_have_required_structure(self):
        """Test that tools have the required structure."""
        for tool in TOOLS:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]


class TestHRAssistAuthentication:
    """Test authentication requirements of HRAssist."""
    
    @patch('hr_assist.OpenAI')
    def test_validate_authentication_valid(self, mock_openai):
        """Test authentication validation with valid ID."""
        agent = HRAssist(openai_api_key="test-key")
        
        assert agent.validate_authentication("EMP-12345") is True
        assert agent.validate_authentication("user123") is True
    
    @patch('hr_assist.OpenAI')
    def test_validate_authentication_invalid(self, mock_openai):
        """Test authentication validation with invalid ID."""
        agent = HRAssist(openai_api_key="test-key")
        
        assert agent.validate_authentication(None) is False
        assert agent.validate_authentication("") is False
        assert agent.validate_authentication("   ") is False
    
    @patch('hr_assist.OpenAI')
    def test_chat_without_authentication(self, mock_openai):
        """Test that chat refuses to operate without authentication."""
        agent = HRAssist(openai_api_key="test-key")
        
        response = agent.chat(
            user_message="What is the PTO policy?",
            authenticated_user_id=None
        )
        
        assert "Authentication required" in response
        assert "authenticated_user_id" in response
    
    @patch('hr_assist.OpenAI')
    def test_chat_with_empty_authentication(self, mock_openai):
        """Test that chat refuses empty authentication."""
        agent = HRAssist(openai_api_key="test-key")
        
        response = agent.chat(
            user_message="What is the PTO policy?",
            authenticated_user_id=""
        )
        
        assert "Authentication required" in response


class TestHRAssistInitialization:
    """Test HRAssist initialization."""
    
    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                HRAssist()
    
    @patch('hr_assist.OpenAI')
    def test_init_with_api_key(self, mock_openai):
        """Test successful initialization with API key."""
        agent = HRAssist(openai_api_key="test-key", company_name="TestCorp")
        
        assert agent.api_key == "test-key"
        assert agent.company_name == "TestCorp"
        assert agent.conversation_history == []
    
    @patch('hr_assist.OpenAI')
    def test_system_prompt_includes_company_name(self, mock_openai):
        """Test that system prompt includes company name."""
        agent = HRAssist(openai_api_key="test-key", company_name="TestCorp")
        
        assert "TestCorp" in agent.system_prompt
    
    @patch('hr_assist.OpenAI')
    def test_system_prompt_has_critical_rules(self, mock_openai):
        """Test that system prompt includes critical rules."""
        agent = HRAssist(openai_api_key="test-key")
        
        assert "authenticated_user_id" in agent.system_prompt
        assert "search_hr_knowledge_base" in agent.system_prompt
        assert "NEVER guess" in agent.system_prompt


class TestHRAssistConversation:
    """Test conversation management."""
    
    @patch('hr_assist.OpenAI')
    def test_reset_conversation(self, mock_openai):
        """Test conversation reset."""
        agent = HRAssist(openai_api_key="test-key")
        agent.conversation_history = [{"role": "user", "content": "test"}]
        
        agent.reset_conversation()
        
        assert agent.conversation_history == []
    
    @patch('hr_assist.OpenAI')
    def test_chat_adds_context_to_message(self, mock_openai):
        """Test that chat adds user context to messages."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent = HRAssist(openai_api_key="test-key")
        
        agent.chat(
            user_message="Hello",
            authenticated_user_id="EMP-12345",
            user_name="John Doe"
        )
        
        # Check that context was added
        assert len(agent.conversation_history) >= 1
        user_message = agent.conversation_history[0]["content"]
        assert "EMP-12345" in user_message
        assert "John Doe" in user_message
        assert "Hello" in user_message


class TestToolParameterValidation:
    """Test that tools have proper parameter validation."""
    
    def test_request_leave_has_all_required_params(self):
        """Test request_leave tool definition has all required parameters."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "request_leave")
        required_params = tool["function"]["parameters"]["required"]
        
        assert "user_id" in required_params
        assert "start_date" in required_params
        assert "end_date" in required_params
        assert "leave_type" in required_params
        assert "reason" in required_params
    
    def test_leave_type_enum_validation(self):
        """Test that leave_type has proper enum values."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "request_leave")
        leave_type_enum = tool["function"]["parameters"]["properties"]["leave_type"]["enum"]
        
        assert "pto" in leave_type_enum
        assert "sick" in leave_type_enum
        assert "unpaid" in leave_type_enum
    
    def test_attendance_status_enum_validation(self):
        """Test that attendance status has proper enum values."""
        tool = next(t for t in TOOLS if t["function"]["name"] == "correct_attendance")
        status_enum = tool["function"]["parameters"]["properties"]["status"]["enum"]
        
        assert "present" in status_enum
        assert "absent" in status_enum
        assert "wfh" in status_enum
        assert "half_day" in status_enum
    
    def test_all_action_tools_require_user_id(self):
        """Test that all action tools require user_id parameter."""
        action_tools = [
            "check_in",
            "check_out",
            "get_leave_balance",
            "request_leave",
            "get_leave_requests",
            "correct_attendance",
            "escalate_to_human_hr"
        ]
        
        for tool_name in action_tools:
            tool = next(t for t in TOOLS if t["function"]["name"] == tool_name)
            required_params = tool["function"]["parameters"]["required"]
            assert "user_id" in required_params, f"{tool_name} should require user_id"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
