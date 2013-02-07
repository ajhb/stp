import serial
import pexpect
import fdpexpect
import sys
import traceback
import time

class TiUsbSwitch:
    serial_info = None
    port_info = {}
    def __init__(self, serial_info={}):
        if not set(['port', 'baudrate', 'bytesize', 'parity', 'stopbits']) <= set(serial_info.keys()):
            raise Exception('Constructor is missing required information, make sure instantiation call complies with: ' +
                                        "{'port':<serial/tty port>,'baudrate' : <bps rate>, 'bytesize': <data bits>, 'parity':<N,O, or E>," + 
                                        "'stopbits':<1,1.5,2>[, 'timeout':<None or # of sec>] [, 'xonxoff':<0 or 1>] [, 'rtscts':<0 or 1>]}")
        
        self.serial_info = serial_info
    
    
    def select_device(self,device):
        try:
            self.select_input(self.port_info[device])
        except KeyError,e:
            raise Exception('Port information for device ' + device + ' has not been entered for the USB switch, via '  +
            '<TiUsbSwitch object>.dev_port_info = {\''+ device +'\':<1 or 2 or ...>} statement.' )
    
    # Select USB Host input to connect to the USB devices. 
    def select_input(self,input):
        try:
            ser_connection = serial.Serial()
            ser_settings = ser_connection.getSettingsDict()
            ser_settings.update(self.serial_info)
            ser_connection.applySettingsDict(ser_settings)
            ser_connection.port = ser_settings['port']
            ser_connection.open()
            usb_expect = fdpexpect.fdspawn(ser_connection)
            usb_expect.sendline(str(input))
            usb_expect.expect('\*', 3)
            usb_expect.close()
        except Exception, e:
            print traceback.format_exc()
            ser_connection.close()
            raise e
    
    def disconnect(self):
        self.select_input(0)



