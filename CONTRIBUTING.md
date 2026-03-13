# Contributing to OpenAgentHub

Thank you for your interest in contributing to **OpenAgentHub**! 🎉

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/OpenAgentHub.git
cd OpenAgentHub
```

### 2. Set up the development environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Run the tests

```bash
pytest tests/ -v
```

### 4. Run the linter

```bash
flake8 api/ cli/ --max-line-length=120
```

## Development Workflow

1. Create a new branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your changes and write tests.
3. Ensure all tests pass and linting is clean.
4. Commit with a meaningful message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add tool categories endpoint
   fix: handle empty tags in search
   docs: update CLI usage examples
   ```
5. Push and open a Pull Request.

## Code Style

- **Max line length**: 120 characters
- **Type hints**: Use them wherever possible
- **Docstrings**: Required for all public functions

## Reporting Issues

- Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template for bugs.
- Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template for ideas.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
