help: ## Show this help
	@echo Usage: make [target]
	@echo
	@echo Targets:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo
.PHONY: help

run: ## Start project (composer packages will be installed automatically)
	docker-compose up -d
	docker exec -it IIS /bin/sh -c "composer install"

cache: ## Clear nette cache
	docker exec -it IIS /bin/sh -c "rm -rf ./temp/cache ./temp/proxies"

stop: ## Stop docker container with project
	docker stop IIS

clean: stop ## Stop and remove container with project
	docker rm IIS