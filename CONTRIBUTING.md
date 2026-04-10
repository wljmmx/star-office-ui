# Contributing to Star Office UI

Thank you for your interest in contributing to Star Office UI! This document provides guidelines for contributing to the project.

## How to Contribute

### 1. Fork the Repository

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/star-office-ui.git
cd star-office-ui
```

### 2. Create a Branch

```bash
# Create a branch for your feature or bugfix
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix-name
```

### 3. Make Your Changes

Follow these guidelines:
- Write clean, readable code
- Add comments where necessary
- Follow the existing code style
- Write tests for new features
- Update documentation

### 4. Run Tests

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-cov

# Run tests
pytest backend/tests/ -v

# Check code style
flake8 backend/
black --check backend/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use Black
- **Linting**: Use flake8
- **Type Hints**: Use mypy for type checking

### Testing

- Write unit tests for all new features
- Maintain at least 80% code coverage
- Use pytest for testing
- Include both positive and negative test cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update API documentation if endpoints change

### Git Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks

Example:
```
feat: add real-time state synchronization

- Implement WebSocket support
- Add state polling fallback
- Update frontend to display real-time updates
```

## Project Structure

```
star-office-ui/
├── backend/
│   ├── api/          # API routes
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   ├── utils/        # Utility functions
│   ├── config/       # Configuration
│   ├── tests/        # Unit tests
│   └── assets/       # Static resources
├── frontend/         # Vue.js frontend
├── .github/          # GitHub workflows
├── Dockerfile        # Docker image
└── docker-compose.yml # Container orchestration
```

## Adding New Features

### 1. New API Endpoint

```python
# backend/api/new_feature.py
from flask import Blueprint, jsonify
from backend.services.database_service import get_db_service

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/api/new-feature', methods=['GET'])
def get_new_feature():
    db = get_db_service()
    data = db.get_new_feature_data()
    return jsonify(data)
```

### 2. New Model

```python
# backend/models/new_model.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class NewModel:
    id: str
    name: str
    status: str
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
```

### 3. New Test

```python
# backend/tests/test_new_feature.py
import pytest
from backend.models.new_model import NewModel

def test_new_model():
    model = NewModel(id="1", name="Test", status="active")
    assert model.to_dict()['name'] == "Test"
```

## Code Review Process

1. Submit your Pull Request
2. Wait for maintainers to review
3. Address any feedback
4. Once approved, your changes will be merged

## Questions?

If you have questions:
- Open an Issue
- Join the discussion
- Contact maintainers

## Thank You!

Your contributions make Star Office UI better for everyone. Thank you for helping out! 🌟
