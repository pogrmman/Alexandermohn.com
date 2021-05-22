from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import pathlib

def make_jinja_params(filename):
    jinja_params = {}
    f = pathlib.Path(filename)
    if f.is_file():
        with f.open(mode = 'r') as data:
            text = data.readlines()
        jinja_params['date'] = datetime.utcfromtimestamp(f.stat().st_ctime)
        jinja_params['modified'] = datetime.utcfromtimestamp(f.stat().st_mtime)
        jinja_params['title'] = text[0].strip().split("Title: ")[1]
        jinja_params['content'] = markdown.markdown("".join(text[1:]))
        return jinja_params
    else:
        raise "That file does not exist!"

