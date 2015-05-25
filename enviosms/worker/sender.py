# -*- coding: UTF-8 -*-
from .modem import Modem
from .message import Message


class Sender(object):
    def __init__(self):
        self._modem = Modem(device)


    def listenMessage(self):
        self._modem.sendMessage()
