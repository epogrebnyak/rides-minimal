"""Sphinx configuration."""
import os, sys

sys.path.insert(0, os.path.abspath("."))

project = "rider"
author = "Evgeniy Pogrebnyak, Stepan Zimin"
copyright = f"2020, {author}"
extensions = ["sphinx.ext.autodoc"]
html_theme = "sphinxdoc"  #'alabaster'
