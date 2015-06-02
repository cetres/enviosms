# -*- coding: UTF-8 -*-
import os
import stat
import serial
import time
import logging

from .exceptions import ModemError

logger = logging.getLogger("enviosms")

class Modem:
    _connected = False
    _message_initialized = False
    _xonxoff = False
    _rtscts = False
    _bytesize = serial.EIGHTBITS
    _parity = serial.PARITY_NONE
    _stopbits = serial.STOPBITS_ONE

    def __init__(self, device, speed=57600, timeout=5):
        self.verify_file(device)
        self._device = device
        self._speed = speed
        self._timeout = timeout

    def verify_file(self, file_name):
        f_mode = os.stat(file_name).st_mode
        if not stat.S_ISCHR(f_mode):
            raise ModemError("Device file is not valid")

    def connect(self):
        if not self._serial:
            self._serial = serial.Serial(self._device,
                                     self._speed,
                                     self._timeout,
                                     xonxoff = self._xonxoff,
                                     rtscts = self._rtscts,
                                     bytesize = self._bytesize,
                                     parity = self._parity,
                                     stopbits = self._stopbits)
            time.sleep(1)

    def flush(self):
        self._serial.flushInput()
        self._serial.flushOutput()

    def read_line(self):
            data = self._serial.readline()
            print data
            return data 

    def send_command(self, command, getline=True, newline=True, expect=None):
            self._serial.write(command)
            if newline:
                self._serial.write("\r")
            if getline or expect:
                data = self.read_ine()
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
