# -*- coding: UTF-8 -*-


class MQError(Exception):
    _errors = {
        1: "Classe com a URI nao encontrada",
        2: "Nao foi possivel realizar conexao na fila",
    }

    def __init__(self, msg=None, cod=0):
        if not msg:
            self.msg = self._errors[cod]
        else:
            self.msg = msg
        self.cod = cod

    def __str__(self):
        return self.msg
