# -*- coding: UTF-8 -*-
from flask import g
from flask.ext.restful import reqparse, abort, Resource, Api

from qpid.messaging import Connection, Message
from qpid.messaging.exceptions import ConnectError

from enviosms.gateway import app, exceptions
from enviosms.gateway.config import Config

MSGS = {}
CONFIG_FILE = 'enviosms_config.py'

def load_config():
    global app, CONFIG_FILE
    conf = Config(app)
    conf.load_config(CONFIG_FILE)
    return conf

@app.before_request
def before_request():
    g.conf = load_config()
    g.logger = g.conf.logger(__name__)

    # https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-apache-qpid
    try:
        g.logger.debug("Starting MQ connection")
        connection = Connection(g.conf.mq_host)
        connection.open()
        session = connection.session()
        sender = session.sender(g.conf.mq_addr)

        parser = reqparse.RequestParser()
        parser.add_argument('msg_num', type=str)
        parser.add_argument('msg_texto', type=str)
    except ConnectError as e:
        raise exceptions.MQError(2)


def abort_if_sms_doesnt_exist(msg_id):
    if msg_id not in MSGS:
        abort(404, message="SMS {} nao existe".format(msg_id))

class Sms(Resource):
    def get(self, msg_id):
        abort_if_todo_doesnt_exist(msg_id)
        return MSGS[msg_id]

    def delete(self, msg_id):
        abort_if_todo_doesnt_exist(msg_id)
        del MSGS[msg_id]
        return '', 204

    def put(self, msg_id):
        args = parser.parse_args()
        msg = {
            'msg_num': args['msg_num'],
        	'msg_texto': args['msg_texto']
        }
        sender.send(Message(msg))
        return msg, 201

class SmsList(Resource):
    def get(self):
        return {'hello': 'world'}

    def put(self, msg_id):
        return {'hello': 'world'}

api = Api(app)
api.add_resource(SmsList, '/')
api.add_resource(Sms, '/sms/<msg_id>')
