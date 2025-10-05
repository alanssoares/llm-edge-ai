# Contributing to LLM Edge AI

Thank you for your interest in contributing to the LLM Edge AI project! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or later
- Docker and Docker Compose
- Git

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/alanssoares/llm-edge-ai.git
   cd llm-edge-ai
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Copy environment variables:**
   ```bash
   cp .env.example .env
   ```

## 📝 Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run formatting before committing:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing

We use pytest for testing. Always write tests for new features.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_simulator.py

# Run specific test
pytest tests/test_simulator.py::TestIoTDeviceSimulator::test_device_initialization
```

### Project Structure

```
llm-edge-ai/
├── src/                      # Source code
│   ├── __init__.py
│   ├── device_simulator.py   # Device simulator
│   ├── mqtt_consumer.py      # MQTT consumer
│   └── generate_compose.py   # Compose generator
├── tests/                    # Test files
├── scripts/                  # Utility scripts
├── config/                   # Configuration files
├── dataset/                  # Data files
└── docs/                     # Documentation
```

## 🔀 Making Changes

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent fixes

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(simulator): add support for custom sensor intervals

Added configuration option to customize sensor reading intervals.
This allows more realistic device simulation patterns.

Closes #123
```

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **Run tests and checks:**
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request on GitHub**

### PR Requirements

- ✅ All tests pass
- ✅ Code is formatted with Black
- ✅ No linting errors
- ✅ New features have tests
- ✅ Documentation is updated
- ✅ Commit messages follow conventions

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description** - Clear description of the issue
2. **Steps to Reproduce** - Detailed steps
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment** - OS, Python version, Docker version
6. **Logs** - Relevant log output

## 💡 Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. **Use Case** - Why is this needed?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other approaches considered
4. **Additional Context** - Screenshots, examples, etc.

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions and classes
- Update inline comments for complex logic
- Create/update documentation in `docs/` for major features

## ❓ Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
