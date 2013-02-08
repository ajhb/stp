import socket
import time

# Class to control the Devantech relay controller http://www.robot-electronics.co.uk/htm/eth_rly16tech.htm
class DevantechRelayController:
    host = None
    port = None
    power_port = None
    
    def __init__(self, controller_info={}):
        if not set(['host', 'port']) <= set(controller_info.keys()):
            raise Exception('Constructor is missing required information, make sure instantiation call complies with: ' +
                                        "{'host':<ip name or address>,'port' = <server port>,  ['power_port':<power port number>}]")
        self.host = controller_info['host']
        self.power_port = controller_info.get('power_port',None)
        self.port = controller_info['port']
    
    # Turns ON/Close Relay at the specified address
    # * address - the port/relay to turn ON
    def switch_on(self,address=None):
        if not self.__switch__('ON', address):
            raise Exception('Turning on port ' + str(address) + ' failed')
    
    # Turns OFF/Open the Relay at the specified address
    # * address - the port/reay to turn OFF
    def switch_off(self,address=None):
        if self.__switch__('OFF', address):
            raise Exception('Turning off port ' + str(address) + ' failed')
    
    # Cycle (Turn OFF and ON) the port/relay at the specified address
    # * address - the port/relay address to cycle
    # * waittime - how long to wait between cycling (default: 5 seconds)
    def reset(self, address=None, waittime=3):
        self.switch_on(address)
        time.sleep(waittime)
        self.switch_off(address)
      
    # * type: either 'ON' or 'OFF'
    # * cmd (byte command of relay)
    def __switch__(self, type, addr):
        status_cmd = 0x5b
        base_add = 0x64
        if type == "OFF":
            base_add = 0x6e
            
        address = addr
        if not addr:
            address = self.power_port
        
        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.settimeout(5)
        sock.send(chr(base_add + address))
        sock.send(chr(status_cmd))
        result = (int(sock.recv(1).encode('hex'),16)  >> (address - 1)) & 0x01
        sock.close()
        return result
