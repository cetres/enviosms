# -*- coding: UTF-8 -*-
'''
Created on 06/06/2015

@author: gustavo
'''

from enviosms.mq import mq_from_url
from enviosms.message import MessageSMS

class SubmitSMS(object):
    def __init__(self, mq_url):
        self._mq = mq_from_url(mq_url)

    def submit(self, recipient, message):
        msg = MessageSMS(recipient, message)
        self._mq.enviar(msg.to_json())