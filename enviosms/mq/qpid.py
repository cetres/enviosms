# -*- coding: UTF-8 -*-
import logging

from enviosms.mq import MQ

logger = logging.getLogger("enviosms")

class Qpid(MQ):
    def _conectar(self):
        self._logger.debug("Regiao AWS: %s" % self._url.netloc)
        self._conn = Connection(self._url.netloc)
        if not self._conn:
            raise MQError(None, 2)
        self._conn.open()
        session = self._conn.session()
        self._sender = session.sender(self._url.path[1:])
        self._receiver = session.receiver(self._url.path[1:])

    def _enviar(self, mensagem):
        m = Message()
        m.set_body(mensagem)
        self._queue.write(m)

    def _receber(self):
        mensagens = self._queue.get_messages(num_messages=1)
        if len(mensagens) == 1:
            self._mensagem = mensagens[0]
            return self._mensagem.get_body()
        return None

    def _tamanho(self):
        self._queue.count()

    def _excluir(self):
        self._queue.delete_message(self._mensagem)
