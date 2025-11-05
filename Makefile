.PHONY: help build serve clean install deploy-github deploy-netlify new-post

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies in virtual environment
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

build: ## Build the static site
	$(PYTHON) build.py
	@echo "✅ Site built in output/"

serve: ## Start local development server
	$(PYTHON) serve.py

clean: ## Clean build artifacts
	rm -rf output/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned build artifacts"

rebuild: clean build ## Clean and rebuild the site

deploy-github: build ## Deploy to GitHub Pages
	$(PYTHON) deploy.py github

deploy-netlify: build ## Deploy to Netlify
	$(PYTHON) deploy.py netlify

new-post: ## Create a new blog post
	@read -p "Post title: " title; \
	slug=$$(echo "$$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g'); \
	date=$$(date +%Y-%m-%d); \
	filename="content/posts/$$date-$$slug.md"; \
	echo "---" > $$filename; \
	echo "title: $$title" >> $$filename; \
	echo "date: $$date" >> $$filename; \
	echo "tags: " >> $$filename; \
	echo "description: " >> $$filename; \
	echo "---" >> $$filename; \
	echo "" >> $$filename; \
	echo "# $$title" >> $$filename; \
	echo "" >> $$filename; \
	echo "Your content here..." >> $$filename; \
	echo "✅ Created $$filename"

watch: ## Watch for changes and rebuild (requires entr)
	@which entr > /dev/null || (echo "Please install entr: apt-get install entr" && exit 1)
	find content templates static -type f | entr -r make build

dev: ## Run development server with auto-rebuild in another terminal
	@echo "Starting development mode..."
	@echo "Server will run on http://localhost:8000"
	@echo "Changes will automatically trigger rebuilds"
	$(MAKE) serve

test: ## Run basic tests
	@echo "Running tests..."
	@$(PYTHON) -c "import build; print('✅ Build script imports successfully')"
	@$(PYTHON) build.py > /dev/null 2>&1 && echo "✅ Build runs without errors" || echo "❌ Build failed"
	@test -f output/index.html && echo "✅ Index page generated" || echo "❌ Index page missing"
	@test -f output/feed.xml && echo "✅ RSS feed generated" || echo "❌ RSS feed missing"

stats: ## Show site statistics
	@echo "📊 Site Statistics:"
	@echo "Posts: $$(ls -1 content/posts/*.md 2>/dev/null | wc -l)"
	@echo "Pages: $$(ls -1 content/pages/*.md 2>/dev/null | wc -l)"
	@echo "Output files: $$(find output -type f 2>/dev/null | wc -l)"
	@echo "Total size: $$(du -sh output 2>/dev/null | cut -f1)"
