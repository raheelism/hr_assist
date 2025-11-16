# HR-Assist

A production-ready, secure, and empathetic HR operations assistant bot for **CompanyName**.

## Overview

HR-Assist is an AI-powered assistant that helps employees with HR-related queries, policies, and operations. It features a React-based frontend and a Python backend powered by LangGraph, with a SQLite database for data persistence. It enforces strict authentication requirements and uses Retrieval-Augmented Generation (RAG) to provide accurate policy information.

## Features

✅ **Full-Stack Application**: React frontend and Python backend
✅ **Secure Authentication**: JWT-based authentication for all API endpoints
✅ **Database Integration**: SQLite database for attendance and leave management
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

2. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend && npm install
```

4. Configure environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OpenAI API key and a secret key
```

## Configuration

Create a `.env` file in the `backend` directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
COMPANY_NAME=CompanyName
SECRET_KEY=your-super-secret-key
```

## Usage

1. Start the backend server:
```bash
python3 backend/app.py
```

2. In a separate terminal, start the frontend server:
```bash
cd frontend && npm start
```

3. Open your browser and navigate to `http://localhost:3000`.

## API Endpoints

- `POST /login`: Authenticates a user and returns a JWT.
- `POST /chat`: Interacts with the HR-Assist agent. Requires a valid JWT in the `x-access-token` header.

## Architecture

### Components

1. **Frontend**: React-based user interface for chat and login.
2. **Backend**: Flask-based REST API with the following components:
    - **Authentication Layer**: Validates JWTs before any operation.
    - **Knowledge Base**: RAG-based search for HR policies and procedures.
    - **Action Tools**: Functions for HR operations (check-in, leave requests, etc.) that interact with the SQLite database.
    - **Agent Logic**: LangGraph-powered conversation manager with tool-calling capabilities.
3. **Database**: SQLite database for storing employee data, attendance records, leave requests, and audit logs.

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

- ✅ JWT-based authentication for all sensitive operations
- ✅ User ID validation before any action
- ✅ No hardcoded credentials or sensitive data
- ✅ Environment-based configuration
- ✅ Audit trail through conversation history

## Testing

Run the backend test suite:

```bash
pytest backend/tests/
```

Run the frontend test suite:

```bash
cd frontend && npm test
```

## Production Deployment

### Considerations

1. **API Key Management**: Use secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
2. **Rate Limiting**: Implement rate limits to prevent abuse
3. **Logging**: Add comprehensive logging for audit trails
4. **Monitoring**: Set up alerts for errors and unusual patterns
5. **Scaling**: Consider using async operations for high concurrency
6. **Database**: Replace SQLite with a more robust database like PostgreSQL or MySQL.

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

### Version 2.0.0 (2025-11-16)
- Migrated to a full-stack application with a React frontend and Python backend.
- Replaced the original agent logic with a LangGraph-powered agent.
- Integrated a SQLite database for data persistence.
- Implemented JWT-based authentication and audit logging.
- Added comprehensive tests for the backend and frontend.
