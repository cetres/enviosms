from flask import Flask

app = Flask(__name__)

from enviosms.gateway import index
