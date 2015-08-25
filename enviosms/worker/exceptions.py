# -*- coding: UTF-8 -*-


class ModemError(Exception):
    _errors = {
        1: "Classe com a URI nao encontrada",
        2: "Nao foi possivel realizar conexao na fila",
    }

    def __init__(self, msg=None, cod=0, msg_modem=None):
        if not msg:
            self.msg = self._errors[cod]
        else:
            self.msg = msg
        self.cod = cod
        self.msg_modem = msg_modem

    def __str__(self):
        return self.msg
