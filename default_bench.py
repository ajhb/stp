# This is the test setup configuration file. It is a python file where all the information regarding the setup of the equipment used for testing is found.
# For each equipment there should be a new EquipmentInfo object instantiated that provides the information.  The EquipmentInfo take two parameter as input:
#         -- the first paramters is the board name used to identify which setup information should be used for testing, by matching the -p command line parameter
#         -- the second parameter is an id used to differentiate two or more boards of the same type. Currently this feature is not implemented but it is there for future use.
#         -- the following properties can be set for each entry:
#               * init_info : A dictionary containing any information required to initilize the equipment. For the TI platform supported in STP this entry must comply with
#                                           {'port':<serial/tty port>,'baudrate' = <bps rate>, 'bytesize' = <data bits>, 'parity':<N,O, or E>, 'stopbits':<1,1.5,2> 
#                                           [, 'timeout':<None or # of sec>] [, 'xonxoff':<0 or 1>] [, 'rtscts':<0 or 1>]}
#               * params: A dictionary containing information related to the setup of the board. Currently the folowing dictionay entries have special
#                               meaning :
#                                   - power_port: A dictionary containing information related to the power switch/relay connection of the board.  Should comply with:
#                                      {<handle of EquipmentInfo entry related to power switch/relay>:<power port used by the board on the switch/relay>}
#               * driver_class_name: A string containing the name of the driver to control the equipment if any.
#               
# During a test a board is selected by matching the parameter passed as -p in the command line with the board name passed to EquipmentInfo.


#Example entry for  Digital logger relay Web controlled DIN relay http://www.digital-loggers.com/din.html
relay_controller = EquipmentInfo('Dl-logger',0)
relay_controller.driver_class_name = 'DlDinRelayController'
relay_controller.init_info = {'host':'192.168.0.100', 'port':80, 'username':'admin','password':'1234'}

#Example entry for  Devantech relay controller http://www.robot-electronics.co.uk/htm/eth_rly16tech.htm
devantech_relay_controller = EquipmentInfo('Devantech',0)
devantech_relay_controller.driver_class_name = 'DevantechRelayController'
devantech_relay_controller.init_info = {'host':'192.168.0.100', 'port':17494}

#Example of TI MSP430 based USB switch
usb_switch = EquipmentInfo('TI-switch',0)
usb_switch.driver_class_name = 'TiUsbSwitch'
usb_switch.init_info = {'port':'/dev/ttyACM0', 'baudrate':9600, 'bytesize':8, 'parity':'N', 'stopbits':1}
usb_switch.params = {'port_info': {'hd':1, 'mmc':2}}

#Examples of board configurations
# This entry defines the setup of an AM335x Starter Kit board
dut = EquipmentInfo("evmskAM335x", "starterware")
# This statement describes the initialization information used to communicate with the board
dut.init_info = {'port':'/dev/ttyUSB1', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
#This statement defined the platform's setup information
dut.params ={'power_port':{devantech_relay_controller:1}, #Specifies the power/reset connection of the board
                                                                                                #this entry must comply with:
                                                                                                # 'power_port': {<power/reset equip handle, devantech in this case >:<port used in the power/reset device>}
                        
                        'usb_info':{'bulk':{'bus': 2, 'idVendor': 0x1cbe , 'idProduct': 0x0003}, #Specifies usb information of the board, USB descriptor information of the board
                                             'msc':'/dev/sd*',                                                                         #Mass Storage class dev node pattern for the board
                                             'switch':usb_switch}}                                                                 #USB switch used by the board must comply with switch:<usb switch handle, TI Switch in this case>

dut = EquipmentInfo("evmAM335x", "starterware")
dut.init_info = {'port':'/dev/ttyS4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}
dut.params ={'power_port':{devantech_relay_controller:2},
                        'usb_info':{'bulk':{'bus': 2, 'idVendor': 0x1cbe , 'idProduct': 0x0003},
                                             'msc':'/dev/sd*',
                                             'switch':usb_switch}}

dut = EquipmentInfo("beaglebone", "starterware")
dut.init_info = {'port':'/dev/ttyUSB4', 'baudrate':115200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0}

