# Test Suite for Star Office UI

## Test Coverage

This test suite covers:

### 1. Database Service Tests (`test_database_service.py`)
- **ConnectionPool Tests**
  - Pool initialization
  - Context manager usage
  - Concurrent connection handling
  
- **DatabaseService Tests**
  - Loading all agents
  - Getting agent by ID
  - Updating agent status
  - Loading all tasks
  - State normalization

- **Singleton Pattern Tests**
  - Singleton instance retrieval
  - Service reset functionality

### 2. API Endpoint Tests (`test_api.py`)
- **Agents API**
  - GET /api/v1/agents
  - GET /api/v1/agents/<id>
  - POST /api/v1/agents/<id>/status
  
- **Tasks API**
  - GET /api/v1/tasks
  
- **State API**
  - GET /api/v1/state
  
- **Assets API**
  - GET /api/v1/assets/positions
  - POST /api/v1/assets/positions
  
- **Config API**
  - GET /api/v1/config
  - POST /api/v1/config
  
- **Join Keys API**
  - GET /api/v1/join-keys

- **API Versioning**
  - /api/version endpoint
  - /health endpoint
  - All endpoints use /api/v1/ prefix

- **Input Validation**
  - Agent status normalization
  - Asset positions validation

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database_service.py -v
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestAgentsAPI -v
```

## Test Coverage Goals

- Database Service: 90%+
- API Endpoints: 85%+
- Validators: 80%+

## Notes

- Tests use temporary in-memory databases
- API tests use Flask test client
- Mock objects are used for external dependencies
