# -*- coding: UTF-8 -*-
from .modem import Modem
import logging

logger = logging.getLogger("enviosms")


class Sender(object):
    def __init__(self, device):
        self._modem = Modem(device)

    def listen_message(self):
        self._modem.send_message()
