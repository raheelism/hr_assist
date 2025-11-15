# HR-Assist Architecture

This document describes the architecture and design decisions for the HR-Assist production-ready system.

## System Overview

HR-Assist is a conversational AI agent built on OpenAI's GPT models with function calling capabilities. It serves as a secure, empathetic interface between employees and HR systems.

```
┌─────────────┐
│   Employee  │
└──────┬──────┘
       │ authenticated_user_id + user_name + message
       ▼
┌─────────────────────────────────────────────────────┐
│              HR-Assist Agent                        │
│  ┌───────────────────────────────────────────────┐ │
│  │  1. Authentication Validation                 │ │
│  │     - Verify authenticated_user_id present    │ │
│  │     - Refuse operation if missing             │ │
│  └───────────────────────────────────────────────┘ │
│                        │                            │
│                        ▼                            │
│  ┌───────────────────────────────────────────────┐ │
│  │  2. OpenAI GPT Model (with System Prompt)    │ │
│  │     - Process user message                    │ │
│  │     - Decide on tool usage                    │ │
│  │     - Generate human responses                │ │
│  └───────────────────────────────────────────────┘ │
│                        │                            │
│                        ▼                            │
│  ┌───────────────────────────────────────────────┐ │
│  │  3. Tool Execution Layer                      │ │
│  │     - Execute selected tools                  │ │
│  │     - Pass authenticated_user_id as user_id   │ │
│  │     - Return structured results               │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│            Backend HR Systems                       │
│  • Knowledge Base (RAG)                             │
│  • Attendance System                                │
│  • Leave Management System                          │
│  • HR Ticketing System                              │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. HRAssist Class

The main agent class that orchestrates all interactions.

**Responsibilities:**
- Initialize OpenAI client
- Manage conversation history
- Validate authentication
- Process user messages
- Handle tool execution
- Generate responses

**Key Methods:**
- `__init__()`: Initialize with API key and company name
- `validate_authentication()`: Enforce authentication requirement
- `chat()`: Main entry point for user interactions
- `_process_response()`: Handle OpenAI responses and tool calls
- `reset_conversation()`: Clear conversation history

### 2. Tool Functions

Eight distinct functions that interface with HR systems:

| Function | Purpose | Parameters | Return |
|----------|---------|------------|--------|
| `search_hr_knowledge_base` | RAG search for policies | query | Found results or not found |
| `check_in` | Record attendance check-in | user_id | Confirmation with ID |
| `check_out` | Record attendance check-out | user_id, note? | Confirmation with ID |
| `get_leave_balance` | Get leave balances | user_id | Balances by type |
| `request_leave` | Submit leave request | user_id, dates, type, reason | Request ID and status |
| `get_leave_requests` | View leave history | user_id, filter? | List of requests |
| `correct_attendance` | Fix attendance record | user_id, date, status, reason | Correction ID |
| `escalate_to_human_hr` | Create HR ticket | user_id, topic, summary | Ticket ID |

**Design Principles:**
- Each function returns a structured dictionary
- All include success status
- All provide IDs for tracking
- All accept user_id as first parameter
- Simulated implementations for demo (replace with real integrations)

### 3. Tool Definitions (TOOLS)

OpenAI function calling format specifications for each tool.

**Structure:**
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Clear description of when to use this tool",
    "parameters": {
      "type": "object",
      "properties": { /* parameter definitions */ },
      "required": [ /* required parameter names */ ]
    }
  }
}
```

**Key Features:**
- Detailed descriptions guide the AI on when to use each tool
- Required parameters are strictly enforced
- Enum values constrain choices (e.g., leave types, statuses)
- user_id required for all action tools

### 4. System Prompt

The system prompt is the AI's instruction manual. It defines:

**Critical Rules:**
1. **Authentication**: Must have authenticated_user_id
2. **Knowledge Source**: Use search_hr_knowledge_base for all policies
3. **No Hallucination**: Never guess or make up information
4. **Parameter Collection**: Get all required params before tool calls
5. **Response Format**: Clear confirmations with IDs and status
6. **Tone**: Professional, concise, friendly, empathetic
7. **Escalation**: Offer human HR when unable to help

### 5. Conversation Flow

**Standard Interaction Pattern:**

```
1. User sends message + authenticated_user_id
   ↓
2. Agent validates authentication
   ↓
3. Agent adds context to message
   ↓
4. OpenAI processes with system prompt + history
   ↓
5. If tool call needed:
   a. Execute tool with parameters
   b. Add result to conversation
   c. Get final response from OpenAI
   ↓
6. Return response to user
   ↓
7. Update conversation history
```

## Security Architecture

### Authentication Layer

**Entry Point Validation:**
- Every `chat()` call checks `authenticated_user_id`
- Refuses operation if missing or empty
- Context prefix added: `[Authenticated User: {id}, Name: {name}]`

**Tool Execution:**
- All action tools receive `user_id` parameter
- ID traced through entire operation chain
- Audit trail via conversation history

**Best Practices:**
- Never trust client-side authentication
- In production, validate token with auth service
- Log all operations with user IDs for auditing

### Data Protection

**Current Implementation:**
- No hardcoded secrets
- API key from environment variables
- No persistent storage of conversations (in-memory only)

**Production Recommendations:**
- Use secret management services (AWS Secrets Manager, Azure Key Vault)
- Encrypt conversation history at rest
- Implement data retention policies
- Add PII detection and masking
- Use TLS for all communications

### Rate Limiting & Abuse Prevention

**Recommended Implementation:**
- Per-user rate limits (e.g., 100 requests/hour)
- Per-IP rate limits
- Exponential backoff for failures
- Monitoring for unusual patterns
- Circuit breakers for backend services

## RAG Architecture

### Current Implementation

The `search_hr_knowledge_base` function currently uses a simulated knowledge base with predefined policies.

**Structure:**
```python
knowledge_base = {
    "topic": {
        "content": "Policy text...",
        "relevance": 0.95
    }
}
```

### Production RAG Implementation

For production, replace with a proper RAG pipeline:

```
User Query
    ↓
1. Query Embedding
   - Convert query to vector using embedding model
   - e.g., OpenAI text-embedding-3-small
    ↓
2. Vector Search
   - Search vector database (Pinecone, Weaviate, Qdrant)
   - Find top-k most similar documents
   - Apply relevance threshold
    ↓
3. Context Retrieval
   - Fetch full document content
   - Include metadata (source, date, version)
    ↓
4. Return to Agent
   - Structured format with content + metadata
   - Agent uses content to answer question
```

**Recommended Tech Stack:**
- **Embedding**: OpenAI text-embedding-3-small or sentence-transformers
- **Vector DB**: Pinecone, Weaviate, or Qdrant
- **Document Processing**: LangChain or LlamaIndex
- **Chunking**: 500-1000 tokens per chunk with overlap
- **Metadata**: Document source, last updated, version, category

## Integration Points

### Backend HR Systems

Replace simulated functions with real integrations:

#### 1. Attendance System
```python
def check_in(user_id: str) -> Dict[str, Any]:
    # Call attendance API
    response = attendance_api.record_check_in(
        employee_id=user_id,
        timestamp=datetime.now(),
        location=get_user_location()
    )
    return format_response(response)
```

#### 2. Leave Management System
```python
def request_leave(user_id, start_date, end_date, leave_type, reason):
    # Call leave management API
    response = leave_api.submit_request(
        employee_id=user_id,
        start_date=parse_date(start_date),
        end_date=parse_date(end_date),
        type=map_leave_type(leave_type),
        reason=reason
    )
    return format_response(response)
```

#### 3. HRIS Integration
```python
def get_leave_balance(user_id: str):
    # Call HRIS API
    response = hris_api.get_employee_balance(
        employee_id=user_id,
        balance_types=['pto', 'sick', 'unpaid']
    )
    return format_response(response)
```

### Authentication Integration

Integrate with your organization's auth system:

```python
def validate_token(token: str) -> Dict[str, Any]:
    """Validate auth token and extract user info."""
    # Call auth service
    response = auth_service.validate(token)
    
    if response.valid:
        return {
            'user_id': response.user_id,
            'name': response.name,
            'email': response.email,
            'roles': response.roles
        }
    return None

# Usage in API endpoint
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_info = validate_token(request.token)
    if not user_info:
        return {"error": "Invalid authentication"}
    
    response = agent.chat(
        user_message=request.message,
        authenticated_user_id=user_info['user_id'],
        user_name=user_info['name']
    )
    return {"response": response}
```

## Scalability Considerations

### Horizontal Scaling

**Stateless Design:**
- Current implementation is stateless (conversation history in memory)
- For production, consider:
  - Redis for conversation state
  - Database for persistent storage
  - Load balancer for multiple instances

### Performance Optimization

**Caching:**
- Cache knowledge base search results (Redis)
- Cache user information (short TTL)
- Cache tool responses where appropriate

**Async Operations:**
- Use async/await for OpenAI calls
- Parallel tool execution where possible
- Background processing for non-urgent tasks

### Monitoring & Observability

**Key Metrics:**
- Request latency (p50, p95, p99)
- Tool execution time
- OpenAI API latency
- Error rates by type
- User satisfaction scores

**Logging:**
- Structured logging (JSON format)
- Request ID for tracing
- User ID for debugging
- Tool calls and parameters
- Errors with stack traces

## Testing Strategy

### Unit Tests
- Tool function correctness
- Parameter validation
- Authentication checks
- Error handling

### Integration Tests
- End-to-end conversation flows
- Tool execution with mocked backends
- Error recovery scenarios

### Manual Testing
- User acceptance testing
- Edge case exploration
- Tone and empathy validation

## Deployment Architecture

### Recommended Stack

```
┌──────────────┐
│  API Gateway │  (Rate limiting, Auth)
└──────┬───────┘
       │
┌──────▼────────────────────┐
│  Application Load Balancer│
└──────┬────────────────────┘
       │
┌──────▼──────┐  ┌──────────┐  ┌──────────┐
│  HR-Assist  │  │ HR-Assist│  │ HR-Assist│
│  Instance 1 │  │Instance 2│  │Instance 3│
└──────┬──────┘  └────┬─────┘  └────┬─────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
┌──────▼──────┐            ┌─────────▼────────┐
│    Redis    │            │  Backend Services│
│ (Sessions)  │            │  (HR Systems)    │
└─────────────┘            └──────────────────┘
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Optional
COMPANY_NAME=CompanyName
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...
```

## Future Enhancements

1. **Multi-language Support**: Detect and respond in user's language
2. **Rich Media**: Handle image uploads (e.g., medical certificates)
3. **Proactive Notifications**: Remind about pending approvals
4. **Analytics Dashboard**: Track usage patterns and satisfaction
5. **Voice Interface**: Integrate with voice assistants
6. **Mobile App**: Native mobile applications
7. **Slack/Teams Integration**: Chat where users already are
8. **Advanced RAG**: Hybrid search (vector + keyword)
9. **Personalization**: Learn user preferences over time
10. **Multi-modal**: Support for structured forms in chat

## Conclusion

HR-Assist is designed with production-readiness in mind:
- ✅ Security-first architecture
- ✅ Scalable design patterns
- ✅ Clear integration points
- ✅ Comprehensive testing
- ✅ Monitoring and observability
- ✅ Documentation and maintainability

The system is ready to be integrated with real HR systems and deployed to production with the recommended enhancements for your specific infrastructure.
