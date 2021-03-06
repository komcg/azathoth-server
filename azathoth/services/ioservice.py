from twisted.application import service
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.python import log

from azathoth.protocols.ioprotocol import IoProtocol
from azathoth.devices.lcd import Lcd
from azathoth.devices.sonar import Sonar

class IoService(service.Service):
    name = "ioservice"
    def __init__(self, port, speed=115200):
        self.port = port
        self.speed = speed
    
    def startService(self):
        log.msg(system='IoService', format="service starting")
        self.protocol = IoProtocol(self)
        log.msg(system='IoService', format="opening serial port %(port)s", port=self.port)
        self.serial = SerialPort(self.protocol, self.port, reactor, baudrate=self.speed)
        self.lcd = Lcd(self)
        self.sonar = Sonar(self)
        self.protocol.register_callback(0x01, self.onHandshake)
        self.protocol.register_callback(0xee, self.onIoError)
        service.Service.startService(self)

    def stopService(self):
        log.msg(system='IoService', format="service stopping")
        self.serial.loseConnection()
        service.Service.stopService(self)

    def onHandshake(self, data):
        log.msg(system='IoService', format="Controller is alive") 
        self.parent.triggerEvent('IO_HANDSHAKE')

    def onIoError(self, data):
        log.msg(system='IoService', format="Controller error, code %(code)#x", code=data[0])
        self.parent.triggerEvent('IO_ERROR', data[0])

