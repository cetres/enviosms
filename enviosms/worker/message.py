

class Message:
    def __init__(self, recipient, content):
        self._recipient = recipient
        self._content = content

    @property
    def recipient(self, number):
        self.recipient = number

    @property
    def content(self, content):
        self.content = content
