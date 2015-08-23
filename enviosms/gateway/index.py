# -*- coding: UTF-8 -*-
from flask import g, jsonify
from flask.ext.restful import reqparse, abort, Resource, Api

from qpid.messaging import Connection, Message
from qpid.messaging.exceptions import ConnectError

from enviosms.gateway import app, exceptions
from enviosms.gateway.config import Config
from enviosms.submitter import SubmitSMS
from enviosms.mq._mq import MQError
from exceptions import InvalidUsage

MSGS = {}
CONFIG_FILE = 'enviosms_config.py'

def load_config():
    global app, CONFIG_FILE
    conf = Config(app)
    conf.load_config(CONFIG_FILE)
    return conf

def request_mq_message():
    # https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-apache-qpid
    try:
        # app.logger.debug("Get MQ request")
        mq_parser = reqparse.RequestParser()
        mq_parser.add_argument('msg_num', help="Num de telefone")
        mq_parser.add_argument('msg_texto', help="Texto da mensagem")
        return mq_parser
    except MQError as err:
        app.logger.error("MQError - %s" % str(err))
        raise InvalidUsage(str(err), status_code=500)

def get_mq():
    mq_sender = g.get('mq_sender', None)
    if not mq_sender:
        # https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-apache-qpid
        try:
            app.logger.debug("Starting MQ connection")
            g.mq_sender = SubmitSMS(app.config["MQ_ADDR"])
            mq_sender = g.mq_sender
        except MQError as err:
            app.logger.error("MQError - %s" % str(err))
            raise InvalidUsage(str(err), status_code=500)
    return mq_sender

@app.before_first_request
def before_first_request():
    g.conf = load_config()
    g.logger = g.conf.logger(__name__)
    app.logger.debug("Config loaded")


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.before_request
def before_request():
    pass


def abort_if_sms_doesnt_exist(msg_id):
    if msg_id not in MSGS:
        abort(404, message="SMS {} nao existe".format(msg_id))


class Sms(Resource):
    def get(self, msg_id):
        app.logger.debug("Getting %s" % msg_id)
        abort_if_sms_doesnt_exist(msg_id)
        return MSGS[msg_id]

    def delete(self, msg_id):
        abort_if_sms_doesnt_exist(msg_id)
        del MSGS[msg_id]
        return '', 204

    def put(self, msg_id):
        mq_parser = request_mq_message()
        args = mq_parser.parse_args()
        msg = {
            'msg_num': args['msg_num'],
            'msg_texto': args['msg_texto']
        }
        g.mq_sender.submit(Message(msg))
        return msg, 201

    def post(self, msg_id):
        mq_sender = get_mq()
        args = request_mq_message().parse_args()
        msg = {
            'msg_id': msg_id or 0,
            'msg_num': args['msg_num'],
            'msg_texto': args['msg_texto']
        }
        app.logger("POST - %(msg_id)s, %(msg_num)s, %(msg_texto)s" % msg)
        # mq_sender.submit(Message(msg))
        mq_sender.submit(args['msg_num'], args['msg_texto'])
        return msg, 201


class SmsList(Resource):
    def get(self):
        mq = get_mq()
        return {'hello': 'world'}


class Status(Resource):
    def get(self):
        pass

api = Api(app)
api.add_resource(SmsList, '/sms/')
api.add_resource(Sms, '/sms/<msg_id>')
