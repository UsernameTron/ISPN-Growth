.PHONY: test test-roi-backend test-roi-frontend test-gcs lint

test: test-roi-backend test-roi-frontend test-gcs
	@echo "All tests passed."

test-roi-backend:
	cd roi-calculator && python -m pytest tests/ -v

test-roi-frontend:
	cd roi-calculator/frontend && npx vitest run

test-gcs:
	cd gcs-engine && python -m pytest tests/ -v

lint:
	cd gcs-engine && ruff check src/
	cd roi-calculator && ruff check api/
