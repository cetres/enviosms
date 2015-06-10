# -*- coding: UTF-8 -*-
import os
import math
import stat
import serial
import time
import binascii

from enviosms._logging import Logging
from .exceptions import ModemError

logger = Logging.getLogger()


class Modem:
    """Modem class for communicating with serial modem"""
    _connected = False
    _message_initialized = False
    _xonxoff = False
    _rtscts = False
    _bytesize = serial.EIGHTBITS
    _parity = serial.PARITY_NONE
    _stopbits = serial.STOPBITS_ONE
    _serial = None
    _pdu_mode = None

    def __init__(self, device, speed=57600, timeout=5):
        """Constructor

        :param device: file name of the device
        :param speed: communication speed intefacing with the device
        :param timeout: seconds for wainting after send a command
        """
        logger.info("Initializing on device %s at speed %s" % (device, speed))
        self.verify_file(device)
        self._device = device
        self._speed = speed
        self._timeout = timeout

    def verify_file(self, file_name):
        """Verify if a file name is a device

        :param file_name: file name of the device
        :return: True if is a device
        """
        f_mode = os.stat(file_name).st_mode
        if not stat.S_ISCHR(f_mode):
            raise ModemError("Device file is not valid")
        return True

    def connect(self):
        """"Connect to the device"""
        if not self._serial:
            self._serial = serial.Serial(
                port = self._device,
                baudrate = self._speed,
                timeout = self._timeout,
                xonxoff = self._xonxoff,
                rtscts = self._rtscts,
                bytesize = self._bytesize,
                parity = self._parity,
                stopbits = self._stopbits
            )
            self.flush()
            time.sleep(1)
            self.init_modem()

    def init_modem(self):
        self.send_command('ATZ')
        self.read()
        self.send_command("ATE0")
        self.read()
        self.flush()

    def flush(self):
        self._serial.flushInput()
        self._serial.flushOutput()

    def _hexlify(self, dados):
       return binascii.hexlify(unicode(dados).encode('utf-16-be'))
       #return binascii.hexlify(unicode(dados).encode('utf-8'))

    def _encodeSemiOctets(self, number):
        if len(number) % 2 == 1:
            number = number + 'F'
        octets = [int(number[i+1] + number[i], 16) for i in xrange(0, len(number), 2)]
        return binascii.hexlify(bytearray(octets)).upper()

    def read(self):
        data = self._serial.readline()
        logger.info("<" + data)
        return data

    def write(self, dados):
       logger.info(">" + str(dados))
       self._serial.write(dados)

    def send_command(self, command, getline=True, newline=True, expect=None):
            try:
                self.write(str(command))
            except:
                raise ModemError("Erro no comando - %s" % command)
            if newline:
                self._serial.write("\r")
            time.sleep(1)
            if getline or expect:
                data = self.read()
                if expect and data != expect:
                    raise ModemError("Return not expected")
                if getline:
                    return data

    def set_pdu_mode(self):
        if self._pdu_mode is not True:
            self.send_command('AT+CMGF=0')
            self._pdu_mode=True

    def set_text_mode(self):
        if self._pdu_mode is not False:
            self.send_command('AT+CMGF=1')
            self._pdu_mode=False

    def init_message(self):
        if not self._message_initialized:
            self.connect()
            self.send_command('AT+CSCS="UCS2"')
            self._message_initialized = True

    def send_message(self, message):
        self.init_message()
        msg_len = len(message.content)
        if msg_len > 160:
            self.set_pdu_mode()
            max_size=67
            msg_count=int(math.ceil(msg_len/float(max_size)))
            for i in range(msg_count):
                m0=i*max_size
                m1=(i+1)*max_size
                if m1 > msg_len:
                    m1=msg_len
                payload_len = m1 - m0
                msg_part = self._hexlify(message.content[m0:m1])
                logger.info("Payload length: %d (%s)" % (payload_len,message.content[m0:m1] ))
                #msg_udh1 = "0011%02X%02X81" % (i, len(message.recipient))
                #msg_udh2 = "0000AA%02X" % (payload_len)
                msg_udh1 = "000100%02X81" % ( len(message.recipient))
                msg_udh2 = "0008%02X" % (payload_len)
                #msg_udh1 = "0041%02X%02X91" % (i, len(message.recipient))
                #msg_udh2 = "0000%02X05000300%02X%02X" % (payload_len,msg_count,i+1)
                destino_so = self._encodeSemiOctets(message.recipient)
                pdu = msg_udh1 + destino_so + msg_udh2 + msg_part
                self.send_command('AT+CMGS="%d"' % ((len(pdu)-2)/2))
                self.write(pdu)
                self.write(chr(26))
                time.sleep(1)
                self.read()
        else:
            self.set_text_mode()
            destino=self._hexlify(message.recipient)
            self.send_command('AT+CMGS="' + destino + '"')
            self.write(self._hexlify(message.content))
            self.write(chr(26))
            time.sleep(1)
            self.read()

    def read_messages(self):
        self.connect()
        self.flush()
        self.send_command('AT+CMGL="REC UNREAD"', getline=True)
        return self._serial.readall()

    def disconnect(self):
        self._serial.close()
        self._serial = None
        self._message_initialized = False
