# -*- coding: UTF-8 -*-
import abc
from urlparse import urlparse
import json
import logging

from ._mq import MQ, MQError
from ._qpid import Qpid
from .sqs import SQS

logger = logging.getLogger("enviosms")


def mq_from_url(url):
    scheme = MQ.urlparse(url).scheme.lower()
    if scheme == "qpid":
        return Qpid(url)
    else:
        logger.debug("Open MQ URL: %s" % url)
        raise MQError("MQ schema not found: %s (URL: %s)" % (scheme, url), 1)

__all__ = ['Qpid', 'MQ', 'SMS', 'MQError', 'mq_from_url']
