from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pathlib
import settings

def make_jinja_params(filename):
    jinja_params = {}
    f = pathlib.Path(filename)
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
        for key, value in jinja_globals:
            self.jinja_env.globals[key] = value

    def render_article(filename, template_name = None):
        if template_name:
            self.article_template = self.jinja_env.get_template(template_name)
        if self.article_template:
            return article_template.render(make_jinja_params(filename))
        else:
            raise "A template to build articles with has not been specified!"

    def render_page(filename, template_name = None):
        if template_name:
            self.page_template = self.jinja_env.get_template(template_name)
        if self.page_template:
            return page_template.render(make_jinja_params(filename))
        else:
            raise "A template to build pages with has not been specified!"

# Create a jinja environment to render the files
jinja_renderer = Renderer("templates", {"SITENAME": settings.SITENAME,
                                        "SITEURL": settings.SITEURL})

        
