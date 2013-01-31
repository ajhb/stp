# This is the test setup configuration file. It is a python file where all the information regarding the setup of the equipment used for testing is found.
# For each equipment there should be a new EquipmentInfo object instantiated that provides the information.  The EquipmentInfo take two parameter as input:
#         -- the first paramters is the board name used to identify which setup information should be used for testing, by matching the -p command line parameter
#         -- the second parameter is an id used to differentiate two or more boards of the same type. Currently this feature is not implemented but it is there for future use.
# During a test a board is selected by matching the parameter passed as -p in the command line with the board name passed to EquipmentInfo.
# Currently, only board serial connection information is supported in the framework.

relay_controller = EquipmentInfo('Dl-logger',0)
relay_controller.driver_class_name = 'DlDinRelayController'
relay_controller.init_info = {'host':'192.168.0.100', 'port':80, 'username':'admin','password':'1234'}

# This entry defines the setup of an AM335x Starter Kit board
dut = EquipmentInfo("evmskAM335x", "starterware")
# This statement describes the serial connection used to communicate with the board
dut.serial_params = {'port':'/dev/ttyUSB5', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
dut.power_port = {relay_controller:2}

dut = EquipmentInfo("evmAM335x", "starterware")
dut.serial_params = {'port':'/dev/ttyS4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
dut.power_port = {relay_controller:3}

dut = EquipmentInfo("beaglebone", "starterware")
dut.serial_params = {'port':'/dev/ttyUSB4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}


