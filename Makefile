.PHONY: help local-up local-down aws-deploy frontend-dev

help:
	@echo "Available commands:"
	@echo "  make local-up       - Start LocalStack environment"
	@echo "  make local-down     - Stop LocalStack environment"
	@echo "  make frontend-dev   - Start frontend dev server"
	@echo "  make aws-deploy     - Deploy to AWS"

local-up:
	docker-compose -f docker-compose.localstack.yml up -d
	@echo "LocalStack environment started"
	@echo "API: http://localhost:8000"
	@echo "LocalStack: http://localhost:4566"

local-down:
	docker-compose -f docker-compose.localstack.yml down

frontend-dev:
	cd frontend && npm run dev

aws-deploy:
	cd terraform && terraform apply
	cd ../frontend && npm run build && aws s3 sync dist/ s3://$(BUCKET_NAME)/ --delete
