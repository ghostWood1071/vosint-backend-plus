import importlib
import os
from glob import glob

from flask import Flask


def register_routes(app: Flask):
    root_pkg_path = "features"
    for path in glob(f"{root_pkg_path}/*"):
        if os.path.isdir(path):
            pkg_uri = path.replace("/", ".")
            pkg = importlib.import_module(pkg_uri)
            app.register_blueprint(pkg.feature)
