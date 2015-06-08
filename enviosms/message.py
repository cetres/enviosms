# -*- coding: UTF-8 -*-
import logging
import json

logger = logging.getLogger("enviosms")

class MessageSMS(object):
    def __init__(self, recipient=None, content=None, json_str=None):
        if json_str:
            data = json.loads(json_str)
            self._recipient = data["recipient"]
            self._content = data["content"]
        else:
            self._recipient = recipient
            self._content = content

    @property
    def recipient(self):
        return self._recipient
    
    @recipient.setter
    def recipient(self, number):
        self._recipient = number

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    def to_json(self):
        return json.dumps({"recipient": self.recipient,
                           "content": self.content})
