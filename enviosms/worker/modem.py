# -*- coding: UTF-8 -*-
import os
import stat
import serial
import time

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
        self._serial = serial.Serial(self._device,
                                     self._speed,
                                     self._timeout,
                                     xonxoff = self._xonxoff,
                                     rtscts = self._rtscts,
                                     bytesize = self._bytesize,
                                     parity = self._parity,
                                     stopbits = self._stopbits)
        time.sleep(1)
        self._connected = True

    def readLine(self):
            data = self._serial.readline()
            print data
            return data 

    def sendCommand(self, command, getline=True, newline=True, expect=None):
            self._serial.write(command)
            if newline:
                self._serial.write("\r")
            if getline or expect:
                data = self.ReadLine()
                if expect and data != expect:
                        raise ModemError("Return not expected")
                if getLine:
                    return data

    def initMessage(self):
        if not self._connected:
            self.connect()
        self.sendCommand('ATZ')
        self.sendCommand('AT+CMGF=1')
        self._message_initialized = True

    def sendMessage(self, message):
        if not self._message_initialized:
            self.initMessage()
        self.sendCommand('AT+CMGS="' + message.recipient + '"', False)
        self.sendCommand(messasge.content, False)
        self._serial.write(chr(26))
        time.sleep(1)

    def disconnect(self):
        self._serial.close()
        self._connected = False
        self._message_initialized = False
