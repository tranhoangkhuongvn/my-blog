#!/usr/bin/env python3
"""
Simple Static Site Generator with Math and Diagram Support
"""
import os
import glob
import shutil
from datetime import datetime
from pathlib import Path
import re
import json

# Try to import markdown, if not available provide instructions
try:
    import markdown
    from markdown.extensions import Extension
    from markdown.preprocessors import Preprocessor
except ImportError:
    print("Error: markdown module not found.")
    print("Please install it with: pip install markdown")
    print("Also recommended: pip install pygments pyyaml")
    exit(1)

# Configuration
SITE_TITLE = "My Technical Blog"
SITE_URL = "https://yourblog.com"
SITE_DESCRIPTION = "A blog about programming, mathematics, and technology"
AUTHOR = "Your Name"

CONTENT_DIR = 'content'
TEMPLATE_DIR = 'templates'
STATIC_DIR = 'static'
OUTPUT_DIR = 'output'

class MathExtension(Extension):
    """Extension to handle LaTeX math expressions for KaTeX"""
    def extendMarkdown(self, md):
        md.preprocessors.register(MathPreprocessor(md), 'math', 25)

class MathPreprocessor(Preprocessor):
    def run(self, lines):
        from markdown.util import AtomicString
        text = '\n'.join(lines)

        # First, protect display math $$...$$ (must be done before inline)
        # Use HTML entities (&#92; = backslash) to prevent Markdown from processing them
        def replace_display_math(m):
            html = f'<div class="math math-display">&#92;[{m.group(1)}&#92;]</div>'
            return AtomicString(html)

        text = re.sub(r'\$\$(.*?)\$\$', replace_display_math, text, flags=re.DOTALL)

        # Then protect inline math $...$
        # Improved regex that handles single characters and avoids greedy matching
        # Match: $ + (non-whitespace char) + (any chars except $) + (non-whitespace char) + $
        # OR: $ + (single non-whitespace, non-$ char) + $
        def replace_inline_math(m):
            html = f'<span class="math math-inline">&#92;({m.group(1)}&#92;)</span>'
            return AtomicString(html)

        text = re.sub(r'\$([^\s\$][^\$]*?[^\s\$]|[^\s\$])\$', replace_inline_math, text)

        # Also handle \(...\) and \[...\] notation
        text = re.sub(r'\\\((.*?)\\\)',
                      lambda m: AtomicString(f'<span class="math math-inline">&#92;({m.group(1)}&#92;)</span>'),
                      text, flags=re.DOTALL)
        text = re.sub(r'\\\[(.*?)\\\]',
                      lambda m: AtomicString(f'<div class="math math-display">&#92;[{m.group(1)}&#92;]</div>'),
                      text, flags=re.DOTALL)

        return text.split('\n')

class MermaidExtension(Extension):
    """Extension to handle Mermaid diagrams"""
    def extendMarkdown(self, md):
        md.preprocessors.register(MermaidPreprocessor(md), 'mermaid', 26)

class MermaidPreprocessor(Preprocessor):
    def run(self, lines):
        text = '\n'.join(lines)
        # Convert ```mermaid blocks to divs
        def replace_mermaid(match):
            code = match.group(1).strip()
            return f'<div class="mermaid">\n{code}\n</div>'
        
        text = re.sub(r'```mermaid\n(.*?)```', replace_mermaid, text, flags=re.DOTALL)
        return text.split('\n')

class Post:
    def __init__(self, filepath):
        self.filepath = filepath
        self.slug = None
        self.title = None
        self.date = None
        self.tags = []
        self.description = ""
        self.content = ""
        self.has_math = False
        self.has_mermaid = False
        self.parse_content()
    
    def parse_content(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse front matter (YAML between ---)
        if content.startswith('---\n'):
            _, fm, content = content.split('---\n', 2)
            self.parse_frontmatter(fm)
        else:
            # Extract metadata from filename
            filename = Path(self.filepath).stem
            match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)', filename)
            if match:
                self.date = datetime.strptime(match.group(1), '%Y-%m-%d')
                self.slug = match.group(2)
                self.title = match.group(2).replace('-', ' ').title()
        
        # Check for math and mermaid content
        if '$' in content or '\\[' in content or '\\(' in content:
            self.has_math = True
        if '```mermaid' in content:
            self.has_mermaid = True
        
        # Configure markdown with extensions
        extensions = ['extra', 'codehilite', 'toc', 'tables', 'fenced_code']
        if self.has_math:
            extensions.append(MathExtension())
        if self.has_mermaid:
            extensions.append(MermaidExtension())
        
        md = markdown.Markdown(extensions=extensions)
        self.content = md.convert(content.strip())
        
        # Extract description (first paragraph)
        if not self.description:
            text = re.sub(r'<[^>]+>', '', self.content)[:200]
            self.description = text.strip() + '...' if len(text) >= 200 else text.strip()
    
    def parse_frontmatter(self, fm):
        """Parse YAML front matter"""
        for line in fm.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'title':
                    self.title = value.strip('"\'')
                elif key == 'date':
                    self.date = datetime.strptime(value.strip('"\''), '%Y-%m-%d')
                elif key == 'slug':
                    self.slug = value.strip('"\'')
                elif key == 'tags':
                    self.tags = [t.strip() for t in value.strip('[]').split(',')]
                elif key == 'description':
                    self.description = value.strip('"\'')
        
        # Generate slug from title if not provided
        if not self.slug and self.title:
            self.slug = re.sub(r'[^\w\s-]', '', self.title.lower())
            self.slug = re.sub(r'[-\s]+', '-', self.slug)

def load_template(name):
    """Load a template file"""
    template_path = Path(TEMPLATE_DIR) / f'{name}.html'
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def render_template(template, **context):
    """Simple template rendering with variable substitution"""
    for key, value in context.items():
        # Handle both {{var}} and {{ var }} syntax
        # Use string replacement instead of regex to avoid issues with special characters
        template = template.replace(f'{{{{{key}}}}}', str(value))
        template = template.replace(f'{{{{ {key} }}}}', str(value))
    return template

def copy_static_files():
    """Copy static files to output directory"""
    if os.path.exists(STATIC_DIR):
        dest = Path(OUTPUT_DIR) / 'static'
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(STATIC_DIR, dest)
        print(f"  ✓ Copied static files")

def generate_post_page(post, templates):
    """Generate individual post page"""
    post_html = render_template(
        templates['post'],
        title=post.title,
        date=post.date.strftime('%B %d, %Y') if post.date else '',
        content=post.content,
        tags=' '.join(f'<span class="tag">{tag}</span>' for tag in post.tags),
        has_math='true' if post.has_math else 'false',
        has_mermaid='true' if post.has_mermaid else 'false'
    )
    
    final_html = render_template(
        templates['base'],
        title=f"{post.title} - {SITE_TITLE}",
        content=post_html,
        site_title=SITE_TITLE,
        has_math='true' if post.has_math else 'false',
        has_mermaid='true' if post.has_mermaid else 'false'
    )
    
    # Create output directory and write file
    output_path = Path(OUTPUT_DIR) / 'posts' / f'{post.slug}.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

def generate_index_page(posts, templates):
    """Generate the index page with recent posts"""
    post_list = []
    for post in posts[:5]:  # Show latest 5 posts
        post_html = f'''
        <article class="post-preview">
            <h2><a href="/posts/{post.slug}.html">{post.title}</a></h2>
            <time datetime="{post.date.isoformat() if post.date else ''}">{post.date.strftime('%B %d, %Y') if post.date else ''}</time>
            <p>{post.description}</p>
            <a href="/posts/{post.slug}.html" class="read-more">Read more →</a>
        </article>
        '''
        post_list.append(post_html)
    
    index_html = render_template(
        templates['index'],
        posts=''.join(post_list),
        site_title=SITE_TITLE,
        site_description=SITE_DESCRIPTION
    )
    
    final_html = render_template(
        templates['base'],
        title=SITE_TITLE,
        content=index_html,
        site_title=SITE_TITLE,
        has_math='false',
        has_mermaid='false'
    )
    
    with open(Path(OUTPUT_DIR) / 'index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

def generate_archive_page(posts, templates):
    """Generate archive page organized by year"""
    posts_by_year = {}
    for post in posts:
        if post.date:
            year = post.date.year
            if year not in posts_by_year:
                posts_by_year[year] = []
            posts_by_year[year].append(post)
    
    archive_html = ['<h1>Archive</h1>']
    for year in sorted(posts_by_year.keys(), reverse=True):
        archive_html.append(f'<h2>{year}</h2>')
        archive_html.append('<ul class="archive-list">')
        for post in posts_by_year[year]:
            date_str = post.date.strftime('%b %d')
            archive_html.append(
                f'<li><span class="date">{date_str}</span> '
                f'<a href="/posts/{post.slug}.html">{post.title}</a></li>'
            )
        archive_html.append('</ul>')
    
    final_html = render_template(
        templates['base'],
        title=f"Archive - {SITE_TITLE}",
        content='\n'.join(archive_html),
        site_title=SITE_TITLE,
        has_math='false',
        has_mermaid='false'
    )
    
    with open(Path(OUTPUT_DIR) / 'archive.html', 'w', encoding='utf-8') as f:
        f.write(final_html)

def generate_rss_feed(posts):
    """Generate RSS feed"""
    rss_items = []
    for post in posts[:10]:  # Latest 10 posts
        pub_date = post.date.strftime('%a, %d %b %Y %H:%M:%S +0000') if post.date else ''
        rss_items.append(f'''
        <item>
            <title>{post.title}</title>
            <link>{SITE_URL}/posts/{post.slug}.html</link>
            <description><![CDATA[{post.description}]]></description>
            <pubDate>{pub_date}</pubDate>
            <guid>{SITE_URL}/posts/{post.slug}.html</guid>
        </item>
        ''')
    
    rss_feed = f'''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>{SITE_TITLE}</title>
            <link>{SITE_URL}</link>
            <description>{SITE_DESCRIPTION}</description>
            <language>en-us</language>
            {''.join(rss_items)}
        </channel>
    </rss>
    '''
    
    with open(Path(OUTPUT_DIR) / 'feed.xml', 'w', encoding='utf-8') as f:
        f.write(rss_feed)

def generate_site():
    """Main function to generate the entire site"""
    print("🚀 Building static site...")
    
    # Clean output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    # Copy static files
    copy_static_files()
    
    # Load templates
    templates = {
        'base': load_template('base'),
        'post': load_template('post'),
        'index': load_template('index')
    }
    
    # Check if templates exist
    if not templates['base']:
        print("⚠️  Warning: No templates found. Creating default templates...")
        create_default_templates()
        templates = {
            'base': load_template('base'),
            'post': load_template('post'),
            'index': load_template('index')
        }
    
    # Process all posts
    posts = []
    post_files = glob.glob(f'{CONTENT_DIR}/posts/*.md')
    
    for filepath in post_files:
        print(f"  ✓ Processing: {Path(filepath).name}")
        post = Post(filepath)
        posts.append(post)
        generate_post_page(post, templates)
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x.date or datetime.min, reverse=True)
    
    # Generate index, archive, and RSS
    if posts:
        generate_index_page(posts, templates)
        generate_archive_page(posts, templates)
        generate_rss_feed(posts)
        print(f"  ✓ Generated index, archive, and RSS feed")
    
    # Process pages
    page_files = glob.glob(f'{CONTENT_DIR}/pages/*.md')
    for filepath in page_files:
        print(f"  ✓ Processing page: {Path(filepath).name}")
        page = Post(filepath)
        
        page_html = render_template(
            templates['post'],
            title=page.title,
            date='',
            content=page.content,
            tags='',
            has_math='true' if page.has_math else 'false',
            has_mermaid='true' if page.has_mermaid else 'false'
        )
        
        final_html = render_template(
            templates['base'],
            title=f"{page.title} - {SITE_TITLE}",
            content=page_html,
            site_title=SITE_TITLE,
            has_math='true' if page.has_math else 'false',
            has_mermaid='true' if page.has_mermaid else 'false'
        )
        
        with open(Path(OUTPUT_DIR) / f'{page.slug}.html', 'w', encoding='utf-8') as f:
            f.write(final_html)
    
    print(f"\n✅ Site built successfully!")
    print(f"   - {len(posts)} posts generated")
    print(f"   - {len(page_files)} pages generated")
    print(f"   - Output in: {OUTPUT_DIR}/")

def create_default_templates():
    """Create default templates if they don't exist"""
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    
    # This function creates templates - they will be created separately
    print("Templates will be created next...")

if __name__ == '__main__':
    generate_site()