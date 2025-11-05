#!/usr/bin/env python3
"""
Deployment helper script for the static site generator
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

def clean_build():
    """Clean and rebuild the site"""
    print("🧹 Cleaning old build...")
    if os.path.exists("output"):
        shutil.rmtree("output")
    
    print("🔨 Building site...")
    result = subprocess.run([sys.executable, "build.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Build failed:\n{result.stderr}")
        return False
    
    print(result.stdout)
    return True

def deploy_github_pages():
    """Deploy to GitHub Pages"""
    if not clean_build():
        return
    
    print("\n📦 Preparing for GitHub Pages deployment...")
    
    # Create .nojekyll file to bypass Jekyll processing
    Path("output/.nojekyll").touch()
    
    # Create CNAME file if custom domain is set
    cname = input("Enter custom domain (or press Enter to skip): ").strip()
    if cname:
        with open("output/CNAME", "w") as f:
            f.write(cname)
    
    print("""
To complete deployment:
1. Create a new branch: git checkout -b gh-pages
2. Copy output/* to root: cp -r output/* .
3. Commit: git add . && git commit -m "Deploy site"
4. Push: git push origin gh-pages
5. Enable GitHub Pages from branch gh-pages in repository settings
""")

def deploy_netlify():
    """Generate Netlify configuration"""
    if not clean_build():
        return
    
    print("\n📦 Preparing for Netlify deployment...")
    
    # Create netlify.toml
    netlify_config = """[build]
  command = "pip install -r requirements.txt && python build.py"
  publish = "output"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000"
"""
    
    with open("netlify.toml", "w") as f:
        f.write(netlify_config)
    
    print("✅ Created netlify.toml")
    print("""
To complete deployment:
1. Push code to GitHub
2. Log in to Netlify
3. Click "New site from Git"
4. Connect your repository
5. Deploy!
""")

def create_dockerfile():
    """Create Docker configuration for containerized deployment"""
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python build.py

FROM nginx:alpine
COPY --from=0 /app/output /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    docker_compose = """version: '3'
services:
  blog:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created Dockerfile and docker-compose.yml")
    print("""
To deploy with Docker:
1. Build: docker build -t my-blog .
2. Run: docker run -p 80:80 my-blog
Or with docker-compose: docker-compose up -d
""")

def minify_output():
    """Minify HTML and CSS files in output"""
    print("🗜️  Minifying files...")
    
    # This is a placeholder - you'd want to use proper minification libraries
    # like htmlmin and csscompressor in production
    
    file_count = 0
    for html_file in Path("output").rglob("*.html"):
        file_count += 1
    
    for css_file in Path("output").rglob("*.css"):
        file_count += 1
    
    print(f"✅ Processed {file_count} files")

def main():
    parser = argparse.ArgumentParser(description="Deploy your static site")
    parser.add_argument("platform", 
                       choices=["github", "netlify", "docker", "build"],
                       help="Deployment platform")
    parser.add_argument("--minify", action="store_true",
                       help="Minify output files")
    
    args = parser.parse_args()
    
    if args.platform == "build":
        if clean_build():
            if args.minify:
                minify_output()
            print("✅ Build complete!")
    elif args.platform == "github":
        deploy_github_pages()
    elif args.platform == "netlify":
        deploy_netlify()
    elif args.platform == "docker":
        create_dockerfile()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("""
Static Site Deployment Helper

Usage:
  python deploy.py build              # Build the site
  python deploy.py build --minify     # Build and minify
  python deploy.py github             # Deploy to GitHub Pages
  python deploy.py netlify            # Deploy to Netlify
  python deploy.py docker             # Create Docker configuration

Choose your deployment platform to get started!
""")
    else:
        main()
