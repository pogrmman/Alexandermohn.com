from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pathlib
import markdown
import settings

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

class Renderer(object):
    def __init__(self, template_path, jinja_globals):
        self.jinja_env = Environment(
            loader = FileSystemLoader(template_path),
            autoescape = select_autoescape(["html","xml"])
            )
        for key in jinja_globals:
            self.jinja_env.globals[key] = jinja_globals[key]

    def render_article(self, filepath, template_name = None):
        if template_name:
            self.article_template = self.jinja_env.get_template(template_name)
        if self.article_template:
            return self.article_template.render(article = make_jinja_params(filepath))
        else:
            raise "A template to build articles with has not been specified!"

    def render_page(self, filepath, template_name = None):
        if template_name:
            self.page_template = self.jinja_env.get_template(template_name)
        if self.page_template:
            return self.page_template.render(page = make_jinja_params(filepath))
        else:
            raise "A template to build pages with has not been specified!"

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
    return files

def file_writer(file_list, renderer, pages_type):
    markdown_files = []
    for f in flatten(file_list):
        if f.suffix == ".md":
            markdown_files.append(f)
    output_files = []
    for f in markdown_files:
        output_files.append(pathlib.Path("output").joinpath(*f.parts[1:]).with_suffix(".html"))
    for i, o in zip(markdown_files, output_files):
        o.parent.mkdir(parents = True, exist_ok = True)
        if pages_type == "article":
            o.write_text(renderer.render_article(i, "article.html"), encoding = "utf-8")
        if pages_type == "page":
            o.write_text(renderer.render_page(i, "page.html"), encoding = "utf-8")

def flatten(lst):
    for item in lst:
        try:
            yield from flatten(item)
        except TypeError:
            yield item
            
# Create a jinja environment to render the files
jinja_renderer = Renderer("templates", {"SITENAME": settings.SITENAME,
                                        "SITEURL": settings.SITEURL})

article_path = pathlib.Path("content/articles")
article_files = walk_dir(article_path)
