.PHONY: install test lint format type-check clean all

# Install development dependencies
install:
	pip install -e ".[dev]"

# Run all tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=ai_paywall --cov-report=html --cov-report=term-missing

# Run linting
lint:
	flake8 ai_paywall tests

# Format code
format:
	black ai_paywall tests
	isort ai_paywall tests

# Type checking
type-check:
	mypy ai_paywall

# Run all quality checks
quality: format lint type-check test

# Clean generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Install pre-commit hooks
pre-commit-install:
	pre-commit install

# Run pre-commit on all files
pre-commit:
	pre-commit run --all-files

# Build package
build: clean
	python -m build

# Install package locally for testing
install-local: build
	pip install dist/*.whl

# Run all checks before commit
all: quality pre-commit

# Help
help:
	@echo "Available targets:"
	@echo "  install          - Install development dependencies"
	@echo "  test             - Run tests"
	@echo "  test-cov         - Run tests with coverage report"
	@echo "  lint             - Run flake8 linting"
	@echo "  format           - Format code with black and isort"
	@echo "  type-check       - Run mypy type checking"
	@echo "  quality          - Run all quality checks"
	@echo "  clean            - Clean generated files"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  pre-commit       - Run pre-commit on all files"
	@echo "  build            - Build package"
	@echo "  install-local    - Install package locally"
	@echo "  all              - Run all checks"
	@echo "  help             - Show this help message"
