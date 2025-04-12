import sys
import os

# Obtém o caminho correto do diretório `src`
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template

app = Flask(__name__)

from . import routes
