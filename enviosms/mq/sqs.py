# -*- coding: UTF-8 -*-

import logging
from boto import sqs
# from boto.sqs.queue import Queue
from boto.sqs.message import Message

from ._mq import MQ, MQError

logger = logging.getLogger("enviosms")


class SQS(MQ):
    def _conectar(self):
        self._logger.debug("Regiao AWS: %s" % self._url.netloc)
        if self._config.has_aws_auth:
            self._logger.debug("Realizando autenticacao completa na AWS")
            self._conn = sqs.connect_to_region(self._url.netloc,
                                               **self._config.aws_auth)
        else:
            self._logger.debug("Realizando autenticacao automatica na AWS")
            self._conn = sqs.connect_to_region(self._url.netloc)
        if not self._conn:
            raise MQError(None, 2)
        self._queue = self._conn.get_queue(self._url.path[1:])

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
