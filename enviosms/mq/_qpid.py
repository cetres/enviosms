# -*- coding: UTF-8 -*-

from enviosms._logging import Logging
from qpid.messaging import Connection, Message
from qpid.messaging.exceptions import ConnectError

from enviosms.mq import MQ, MQError

logger = Logging.getLogger()


class Qpid(MQ):
    _timeout = 1

    def _conectar(self):
        try:
            logger.debug("Qpid: %s" % self._url.netloc)
            self._conn = Connection(self._url.netloc)
            if not self._conn:
                raise MQError(None, 2)
            self._conn.open()
            self._session = self._conn.session()
            self._sender = self._session.sender(self._url.path[1:])
            self._receiver = self._session.receiver(self._url.path[1:])
            logger.debug("Connected on queue %s" % self._url.netloc)
        except ConnectError:
            raise MQError(cod=2)

    def _enviar(self, mensagem):
        logger.debug("Sending a message")
        m = Message(mensagem)
        self._sender.send(m, True, self._timeout)

    def _receber(self, timeout=None):
        logger.debug("Retrieving a message")
        self._mensagem = self._receiver.fetch(timeout)
        return self._mensagem.content

    def _tamanho(self):
        self._receiver.available()

    def _excluir(self):
        logger.debug("Ack last message")
        self._session.acknowledge()

    def _terminar(self):
        self._conn.close(self._timeout)
