from flask import Flask

app = Flask(__name__)
from sms import index
