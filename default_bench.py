# This is the test setup configuration file. It is a python file where all the information regarding the setup of the equipment used for testing is found.
# For each equipment there should be a new EquipmentInfo object instantiated that provides the information.  The EquipmentInfo take two parameter as input:
#         -- the first paramters is the board name used to identify which setup information should be used for testing, by matching the -p command line parameter
#         -- the second parameter is an id used to differentiate two or more boards of the same type. Currently this feature is not implemented but it is there for future use.
#         -- the following properties can be set for each entry:
#               * serial_params : A dictionary containing serial connectivity information for the equipment. Should comply with:
#                                           {'port':<serial/tty port>,'baudrate' = <bps rate>, 'bytesize' = <data bits>, 'parity':<N,O, or E>, 'stopbits':<1,1.5,2> 
#                                           [, 'timeout':<None or # of sec>] [, 'xonxoff':<0 or 1>] [, 'rtscts':<0 or 1>]}
#               * power_port: A dictionary containing information related to the power switch/relay connection of the board.  Should comply with:
#                                      {<handle of EquipmentInfo entry related to power switch/relay>:<power port used by the board on the switch/relay>}
#               * driver_class_name: A string containing the name of the driver to control the equipment if any.
#               * init_info: A dictionary containing any information required to initilize the driver specified in driver_class_name.
# During a test a board is selected by matching the parameter passed as -p in the command line with the board name passed to EquipmentInfo.


#Example entry for  Digital logger relay Web controlled DIN relay http://www.digital-loggers.com/din.html
relay_controller = EquipmentInfo('Dl-logger',0)
relay_controller.driver_class_name = 'DlDinRelayController'
relay_controller.init_info = {'host':'192.168.0.100', 'port':80, 'username':'admin','password':'1234'}

#Examples of board configurations
# This entry defines the setup of an AM335x Starter Kit board
dut = EquipmentInfo("evmskAM335x", "starterware")
# This statement describes the serial connection used to communicate with the board
dut.serial_params = {'port':'/dev/ttyUSB5', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
# This statement describes the power connection of the board. In this case implies that this board is connected to port 2 on the relay_controller defined above. 
dut.power_port = {relay_controller:2}

dut = EquipmentInfo("evmAM335x", "starterware")
dut.serial_params = {'port':'/dev/ttyS4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
dut.power_port = {relay_controller:3}

dut = EquipmentInfo("beaglebone", "starterware")
dut.serial_params = {'port':'/dev/ttyUSB4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}


