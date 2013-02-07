import httplib
import time
import base64

# Class to control the Web controlled DIN relay http://www.digital-loggers.com/din.html
class DlDinRelayController:
    host = None
    port = None
    password = None
    username = None
    power_port = None
    def __init__(self, controller_info={}):
        if not set(['host', 'port', 'username', 'password']) <= set(controller_info.keys()):
            raise Exception('Constructor is missing required information, make sure instantiation call complies with: ' +
                                        "{'host':<ip name or address>,'port': <server port>, 'username': <username>, 'password':<password> ['power_port':<power port number>}]")
        self.host = controller_info['host']
        self.power_port = controller_info.get('power_port',None)
        self.port = controller_info['port']
        self.username = controller_info['username']
        self.password = controller_info['password']
    
    
    # Turns ON/Close Relay at the specified address
    # * address - the port/relay to turn ON
    def switch_on(self,address=None):
        self.__switch__("ON", address)
    
    # Turns OFF/Open the Relay at the specified address
    # * address - the port/reay to turn OFF
    def switch_off(self,address=None):
        self.__switch__("OFF", address)
    
    # Cycle (Turn OFF and ON) the port/relay at the specified address
    # * address - the port/relay address to cycle
    # * waittime - how long to wait between cycling (default: 5 seconds)
    def reset(self, address=None, waittime=3):
        self.switch_on(address)
        time.sleep(waittime)
        self.switch_off(address)
      
    # * type: either 'ON' or 'OFF'
    # * address - 0-7 (Address of relay)
    def __switch__(self, type, addr):
        address = addr
        if not addr:
            address = self.power_port
            
        dl_connection = httplib.HTTPConnection(self.host, self.port, timeout=10)
        for i in range(0,3):
            dl_connection.request('GET','/outlet?' + str(address) + '=' + type.upper() , None,{'Authorization':'Basic ' + base64.b64encode(self.username + ':' + self.password).strip()})
            response = dl_connection.getresponse()
            if response.status == 200:
                break
        else:
            raise Exception(response.reason)
