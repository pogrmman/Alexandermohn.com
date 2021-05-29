from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pathlib
import shutil
import markdown
import settings

### Classes ###
# Class for rendering 
class Renderer(object):
    def __init__(self, template_path, jinja_globals):
        self.jinja_env = Environment(
            loader = FileSystemLoader(template_path),
            autoescape = select_autoescape(["html","xml"])
            )
        for key in jinja_globals:
            self.jinja_env.globals[key] = jinja_globals[key]

    def render_article(self, jinja_params, template_name = None):
        if template_name:
            self.article_template = self.jinja_env.get_template(template_name)
        if self.article_template:
            return self.article_template.render(article = jinja_params)
        else:
            raise "A template to build articles with has not been specified!"

    def render_page(self, jinja_params, template_name = None):
        if template_name:
            self.page_template = self.jinja_env.get_template(template_name)
        if self.page_template:
            return self.page_template.render(page = jinja_params)
        else:
            raise "A template to build pages with has not been specified!"

### Functions ###
# Take a markdown file and prepare it for rendering with jinja
def make_jinja_params(filepath):
    jinja_params = {}
    f = pathlib.Path(filepath)
    if f.is_file():
        with f.open(mode = "r") as data:
            text = data.readlines()
        jinja_params["date"] = datetime.utcfromtimestamp(f.stat().st_ctime)
        jinja_params["modified"] = datetime.utcfromtimestamp(f.stat().st_mtime)
        jinja_params["title"] = text[0].strip().split("Title: ")[1]
        jinja_params["content"] = markdown.markdown("".join(text[1:]))
        return jinja_params
    else:
        raise "That file does not exist!"

# Walk a directory, building up a list of paths in that directory
def walk_dir(path):
    files = []
    directories = []
    for child in path.iterdir():
        if child.is_dir():
            directories.append(child)
        elif child.is_file():
            files.append(child)
    for directory in directories:
        files_in_dir = walk_dir(directory)
        if files_in_dir:
            files.append(files_in_dir)
    return list(flatten(files))

# Take a list of files, render the markdown files and make corresponding html files in output
def file_writer(html_path, renderer, pages_type):
    for page in html_path:
        i = page[0]
        o = page[1]
        o.parent.mkdir(parents = True, exist_ok = True)
        if pages_type == "article":
            o.write_text(renderer.render_article(i, "article.html"), encoding = "utf-8")
        if pages_type == "page":
            o.write_text(renderer.render_page(i, "page.html"), encoding = "utf-8")

# Make HTML file paths
def make_HTML(paths):
    markdown_files = []
    for f in paths:
        if f.suffix == ".md":
            markdown_files.append(f)
    output_files = []
    for f in markdown_files:
        output_files.append(pathlib.Path("output").joinpath(*f.parts[1:]).with_suffix(".html"))
    return_list = []
    for i, o in zip(markdown_files, output_files):
        return_list.append([make_jinja_params(i), o])
    return_list.sort(key = lambda x: x[0]["date"])
    return return_list

# Generator to flatten nested lists
def flatten(lst):
    for item in lst:
        try:
            yield from flatten(item)
        except TypeError:
            yield item

# Test if one path is a child of another
def is_child(child, parent):
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False

# Copy static files to output directory
def copy_statics(static_content):
    for f in static_content:
        output_path = pathlib.Path("output").joinpath(*f.parts[1:])
        output_path.parent.mkdir(parents = True, exist_ok = True)
        shutil.copy(f, output_path)
        
### Build Script ###
if __name__ == "__main__":
    # Get a list of all content
    all_files = walk_dir(pathlib.Path("content"))
    article_path = pathlib.Path("content/articles")
    page_path = pathlib.Path("content/pages")
    static_path = pathlib.Path("content/static")
    articles = [f for f in all_files if is_child(f, article_path)]
    pages = [f for f in all_files if is_child(f, page_path)]
    statics = [f for f in all_files if is_child(f, static_path)]
    # Generate HTML files
    jinja_renderer = Renderer("templates", {"SITENAME": settings.SITENAME,
                                            "SITEURL": settings.SITEURL,
                                            "STATICDIR": settings.STATICDIR})
    articles = make_HTML(articles)
    pages = make_HTML(pages)
    file_writer(articles, jinja_renderer, "article")
    file_writer(pages, jinja_renderer, "page")
    # Copy static content
    copy_statics(statics)
    # Copy css
    css_path = pathlib.Path("static/css")
    output_css_path = pathlib.Path("output/static/css")
    if output_css_path.exists():
        shutil.rmtree(output_css_path)
    shutil.copytree(css_path, output_css_path)
