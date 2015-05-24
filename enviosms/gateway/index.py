from enviosms import app
from flask.ext.restful import reqparse, abort, Resource, Api
from qpid.messaging import Connection, Message

BROKER = "localhost:5672" 
ADDRESS = "sms.sender"
MSGS = {}

# https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-apache-qpid
connection = Connection(BROKER)
connection.open()
session = connection.session()
sender = session.sender(address)

parser = reqparse.RequestParser()
parser.add_argument('msg_num', type=str)
parser.add_argument('msg_texto', type=str)

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
