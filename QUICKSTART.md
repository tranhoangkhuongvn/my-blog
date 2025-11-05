# 🚀 Quick Start Guide

Welcome to your new static site generator blog!

## Installation (One-Time Setup)

### macOS / Linux:
```bash
chmod +x setup.sh
./setup.sh
```

### Windows:
```cmd
setup.bat
```

## Daily Usage

### macOS / Linux:

```bash
# Build the site
make build
# OR
./venv/bin/python build.py

# Preview locally (http://localhost:8000)
make serve
# OR
./venv/bin/python serve.py

# Create a new post
make new-post
```

### Windows:

```cmd
# Activate virtual environment first
venv\Scripts\activate

# Build the site
python build.py

# Preview locally (http://localhost:8000)
python serve.py
```

## Creating Posts

1. Create a new file in `content/posts/` with format: `YYYY-MM-DD-title.md`
2. Add front matter:
```yaml
---
title: Your Post Title
date: 2024-11-04
tags: tag1, tag2
description: Brief description
---
```
3. Write your content in Markdown
4. Build the site: `python build.py`
5. Preview: `python serve.py`

## Features

✅ **Theme Toggle**: Click the sun/moon icon to switch between dark and light themes

✅ **Math Support**: Use `$E=mc^2$` for inline or `$$E=mc^2$$` for display math

✅ **Code Blocks**: Use triple backticks with language name
```python
def hello():
    print("Hello, World!")
```

✅ **Mermaid Diagrams**: Use triple backticks with 'mermaid'

## Deployment

- **GitHub Pages**: See `deploy.py github`
- **Netlify**: See `deploy.py netlify`
- **Traditional Host**: Upload the `output/` folder

## Need Help?

- Full documentation: `README.md`
- Example posts in: `content/posts/`
- Templates in: `templates/`
- Styling in: `static/style.css`

Happy blogging! 🎉
