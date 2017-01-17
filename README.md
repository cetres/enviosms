# enviosms
SMS sender

This package can send SMS through a USB 3g/4g dongle. It was tested with Huawei Modem E367 (12d1:1506) and CentOS 7.2
but it may work with others similar modems.

Required dependencies:
* usb_modeswitch (usb modem context switch)
* qpid-cpp-server (AMQP)
* qpid-cpp-client

Before start execute the following command to create a persistent queue:
```
/usr/bin/qpid-config add queue sms.sender --durable
```
