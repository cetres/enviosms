# -*- coding: UTF-8 -*-
import os
import math
import stat
import serial
import time
import binascii
from random import randint

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
    _msg_send_time = 0               # Last message duration time to send
    _mr = -1                         # Message reference number

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
                port=self._device,
                baudrate=self._speed,
                timeout=self._timeout,
                xonxoff=self._xonxoff,
                rtscts=self._rtscts,
                bytesize=self._bytesize,
                parity=self._parity,
                stopbits=self._stopbits
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

    @property
    def mr(self):
        self._mr += 1
        if self._mr > 255:
            self._mr = 0
        return self._mr

    def _hexlify(self, dados):
        return binascii.hexlify(unicode(dados).encode('utf-16-be')).upper()

    def _encodeSemiOctets(self, number):
        if number[0] == '+':
            number = number[1:]
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

    def send_command(self, command, getline=True, newline=True, append=None, expect=None, timeout=3):
            self.flush()
            try:
                self.write(str(command))
                if append:
                    self.write(append)
            except:
                raise ModemError("Erro no comando - %s" % command)
            if newline:
                self._serial.write("\r")
            if getline or expect:
                data = self.read().strip()
                if expect:
                    for _ in range(0, timeout):
                        if len(data) == 0:
                            time.sleep(1)
                            data = self.read().strip()
                        else:
                            break
                    if not data.startswith(expect):
                        raise ModemError("Return not expected (%s) of (%s)" % (data, expect), msg_modem=data)
                if getline:
                    return data

    def set_pdu_mode(self):
        if self._pdu_mode is not True:
            self.send_command('AT+CMGF=0', expect="OK")
            self._pdu_mode = True

    def set_text_mode(self):
        if self._pdu_mode is not False:
            self.send_command('AT+CMGF=1', expect="OK")
            self._pdu_mode = False

    def init_message(self):
        if not self._message_initialized:
            self.connect()
            self.send_command('AT+CSCS="UCS2"', expect="OK")
            self._message_initialized = True

    def send_message(self, message, force_pdu=False, force_udh=False, tp_vpf=None):
        t0 = time.time()
        self.init_message()
        logger.info("Recipient: %s" % message.recipient)
        if not message.content:
            logger.error("Mensagem sem conteudo")
            return True
        msg_len = len(message.content)
        if msg_len > 160 or force_pdu:
            self.set_pdu_mode()
            tp_class = 0x01
            dcs = 0x08
            if tp_vpf is not None:
                tp_class |= 0x10
                tp_vpf = "%02X" % tp_vpf
            else:
                tp_vpf = ""
            max_size = 60
            msg_count = int(math.ceil(msg_len/float(max_size)))
            ref_number = randint(0, 255)
            for i in range(msg_count):
                m0 = i*max_size
                m1 = (i+1)*max_size
                if m1 > msg_len:
                    m1 = msg_len
                msg_part = self._hexlify(message.content[m0:m1])
                udl = len(msg_part)/2
                logger.info("Payload length: %d (%s)" % (udl, message.content[m0:m1] ))
                rcpt = message.recipient
                if rcpt[0] == '+':
                    num_type = 0x91
                    rcpt = rcpt[1:]
                else:
                    num_type = 0x81
                if msg_count > 1 or force_udh:
                    tp_class |= 0x40
                    tpdu1 = "00%02X%02X%02X%02X" % (tp_class, self.mr, len(rcpt), num_type)
                    udh = "050003%02X%02X%02X" % (ref_number, msg_count, i+1)
                    udl += len(udh)/2
                    tpdu2 = "00%02X%s%02X%s" % (dcs, tp_vpf, udl, udh)
                else:
                    tpdu1 = "00%02X%02X%02X%02X" % (tp_class, self.mr, len(rcpt), num_type)
                    tpdu2 = "00%02X%s%02X" % (dcs, tp_vpf, udl)

                logger.info("TP: %02X DCS: %02X UDL: %02X (%d)" % (tp_class, dcs, udl, udl))
                destino_so = self._encodeSemiOctets(rcpt)
                pdu = tpdu1 + destino_so + tpdu2 + msg_part
                self.send_command('AT+CMGS=%d' % ((len(pdu)-2)/2), expect=">")
                try:
                    self.send_command(pdu, newline=False,  append=chr(26), expect="+CMGS", timeout=30)
                except ModemError as e:
                    if e.msg_modem == "+CMS ERROR: 500":
                        logger.warn("Message not sent: %s" % e.msg_modem)
                        return False
                    else:
                        raise
        else:
            self.set_text_mode()
            destino = self._hexlify(message.recipient)
            self.send_command('AT+CMGS="' + destino + '"')
            self.write(self._hexlify(message.content))
            self.write(chr(26))
            time.sleep(1)
            self.read()
        self._msg_send_time = time.time() - t0
        logger.info("Time: %.1f sec" % self._msg_send_time)
        return True

    def read_messages(self):
        self.connect()
        self.flush()
        self.send_command('AT+CMGL="REC UNREAD"', getline=True)
        return self._serial.readall()

    def disconnect(self):
        self._serial.close()
        self._serial = None
        self._message_initialized = False
