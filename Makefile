.PHONY: test install dev clean help

help:
	@echo "SpiceflowNavigator-Pipeline Development Commands"
	@echo "================================"
	@echo ""
	@echo "  test     Run tests"
	@echo "  install  Install dependencies"
	@echo "  dev      Start development server"
	@echo "  clean    Clean temporary files"

test:
	pytest tests/ -v

install:
	pip install -r requirements.txt

dev:
	python cli.py --help

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
