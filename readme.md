# HR-Assist

A production-ready, secure, and empathetic HR operations assistant bot for **CompanyName**.

## Overview

HR-Assist is an AI-powered assistant that helps employees with HR-related queries, policies, and operations. It enforces strict authentication requirements and uses Retrieval-Augmented Generation (RAG) to provide accurate policy information.

## Features

✅ **Secure Authentication**: Requires `authenticated_user_id` with every request  
✅ **RAG-Based Knowledge**: Uses `search_hr_knowledge_base` for all policy questions  
✅ **Comprehensive HR Operations**:
  - Check-in/check-out tracking
  - Leave balance inquiries
  - Leave request submission
  - Attendance corrections
  - Human HR escalation

✅ **Professional & Empathetic**: Maintains a friendly, professional tone  
✅ **No Hallucinations**: Only provides information from the knowledge base

## Installation

1. Clone the repository:
```bash
git clone https://github.com/raheelism/hr_assist.git
cd hr_assist
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
COMPANY_NAME=CompanyName
```

## Usage

### Command Line Interface

Run the interactive CLI:

```bash
python hr_assist.py
```

You'll be prompted for your user ID and name, then you can start asking questions!

### Programmatic Usage

```python
from hr_assist import HRAssist

# Initialize the agent
agent = HRAssist(company_name="CompanyName")

# Chat with authentication
response = agent.chat(
    user_message="What is the PTO policy?",
    authenticated_user_id="EMP-12345",
    user_name="John Doe"
)

print(response)
```

## Example Conversations

### Checking Leave Balance

```
You: What is my leave balance?
HR-Assist: Let me check your current leave balance.

Your leave balance as of 2025-11-15:
• PTO: 12.5 days available (2.5 used out of 15.0 total)
• Sick Leave: 8.0 days available (2.0 used out of 10.0 total)
• Unpaid Leave: Unlimited (0 used)

Is there anything specific about your leave balance you'd like to know?
```

### Requesting Leave

```
You: I need to request PTO for December 20-27
HR-Assist: I'd be happy to help you submit a leave request. I need a bit more information:

Could you please provide the reason for your leave request?

You: Holiday vacation
HR-Assist: Perfect! I've submitted your leave request:

✅ Request ID: LR-EMP12345-20251115143022
📅 Dates: December 20, 2023 - December 27, 2023
📝 Type: PTO (Paid Time Off)
📋 Reason: Holiday vacation
⏳ Status: Pending approval

Your manager will review this request. You'll receive a notification once it's been processed.
```

### Policy Questions

```
You: What is the remote work policy?
HR-Assist: Based on our remote work policy:

Employees may work remotely up to 2 days per week with manager approval. 
Full-time remote arrangements require VP approval. You're also eligible for 
an equipment stipend of $500 annually for home office setup.

Would you like more details or have questions about implementing this?
```

### Without Authentication

```
You: What is the PTO policy?
HR-Assist: ❌ Authentication required. I cannot assist without your authenticated 
user ID. Please provide your authenticated_user_id to continue.
```

## Architecture

### Components

1. **Authentication Layer**: Validates `authenticated_user_id` before any operation
2. **Knowledge Base**: RAG-based search for HR policies and procedures
3. **Action Tools**: Functions for HR operations (check-in, leave requests, etc.)
4. **Agent Logic**: OpenAI-powered conversation manager with function calling
5. **Response Handler**: Processes tool outputs and generates user-friendly responses

### Tool Functions

| Tool | Purpose | Required Parameters |
|------|---------|---------------------|
| `search_hr_knowledge_base` | Search HR policies | `query` |
| `check_in` | Record check-in | `user_id` |
| `check_out` | Record check-out | `user_id`, `note` (optional) |
| `get_leave_balance` | Get leave balances | `user_id` |
| `request_leave` | Submit leave request | `user_id`, `start_date`, `end_date`, `leave_type`, `reason` |
| `get_leave_requests` | View leave history | `user_id`, `filter_status` (optional) |
| `correct_attendance` | Fix attendance | `user_id`, `date`, `status`, `reason` |
| `escalate_to_human_hr` | Escalate to human | `user_id`, `topic`, `chat_history_summary` |

### Security Features

- ✅ Mandatory authentication for all operations
- ✅ User ID validation before any action
- ✅ No hardcoded credentials or sensitive data
- ✅ Environment-based configuration
- ✅ Audit trail through conversation history

## Testing

Run the test suite:

```bash
pytest tests/
```

Run specific tests:

```bash
pytest tests/test_hr_assist.py -v
```

## Production Deployment

### Considerations

1. **API Key Management**: Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
2. **Rate Limiting**: Implement rate limits to prevent abuse
3. **Logging**: Add comprehensive logging for audit trails
4. **Monitoring**: Set up alerts for errors and unusual patterns
5. **Scaling**: Consider using async operations for high concurrency
6. **Database Integration**: Replace simulated data with actual HR system connections

### Integration Points

To connect to real HR systems, replace the simulated functions in `hr_assist.py`:

```python
# Replace simulated implementation with actual API calls
def get_leave_balance(user_id: str) -> Dict[str, Any]:
    # Call your HR system API
    response = hr_system_api.get_balance(user_id)
    return response
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
- Open an issue on GitHub
- Contact the development team
- Refer to the internal documentation

## Changelog

### Version 1.0.0 (2025-11-15)
- Initial production release
- Core HR operations support
- RAG-based knowledge search
- Authentication enforcement
- Comprehensive tool suite
