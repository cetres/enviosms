# -*- coding: UTF-8 -*-
import os
import stat
import serial
import time

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
            time.sleep(1)

    def flush(self):
        self._serial.flushInput()
        self._serial.flushOutput()

    def read_line(self):
            data = self._serial.readline()
            logger.debug("<" + data)
            return data

    def send_command(self, command, getline=True, newline=True, expect=None):
            try:
                logger.debug(">" + str(command))
                self._serial.write(str(command))
            except:
                raise ModemError("Erro no comando - %s" % command)
            if newline:
                self._serial.write("\r")
            if getline or expect:
                data = self.read_line()
                if expect and data != expect:
                    raise ModemError("Return not expected")
                if getline:
                    return data

    def init_message(self):
        if not self._message_initialized:
            self.connect()
            self.send_command('ATZ')
            self.send_command('AT+CMGF=1')
            self._message_initialized = True

    def send_message(self, message):
        self.init_message()
        self.send_command('AT+CMGS="' + message.recipient + '"', False)
        self.send_command(message.content, False)
        self._serial.write(chr(26))
        time.sleep(1)

    def read_messages(self):
        self.connect()
        self.flush()
        self.send_command('AT+CMGL="REC UNREAD"', getline=True)
        return self._serial.readall()

    def disconnect(self):
        self._serial.close()
        self._serial = None
        self._message_initialized = False
