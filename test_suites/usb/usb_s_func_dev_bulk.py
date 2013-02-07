# @desc USB-DEV-BULK example test. Verifies basic bulk functionality on the device.
# The test is based on PyUSB 1.0 or later which can be downloaded from 
# http://sourceforge.net/projects/pyusb/ and installed, "sudo apt-get install python-usb" 
# installs 0.4 which does not support the PyUSB API used here.
# Before running this test Make sure the device has been installed successfully. 
# For Linux systems also make sure there is a rule with the appropriate mode 
# (SUBSYSTEM=="usb", ATTR{idVendor}=="<your Vendor ID>", ATTR{idProduct}=="<your product ID>", MODE="666")
# in one of the files located at /etc/udev/rules.d/
# The code presented here is based on the PyUSB tutorial http://pyusb.sourceforge.net/docs/1.0/tutorial.html
# WARNING: Currently all the boards from the same SoC family have the same Vendor ID and product ID so
# it the device has to be detected by the difference betweem preboot and post boot information.
# Even then there is chance that if two instances of STP are running this testcase
# or a test case with this functionality at the same time, then the device detected 
# might be the wrong device.

requires = ['usb']

import usb.core
import usb.util
import string
import re
import time


# START OF TEST LOGIC
if power_controller:
    power_controller.switch_on()
else:
    print 'Press and hold reset button now....'

time.sleep(3)
preboot_usb_list = usb.core.find(find_all=True, bus=platform_setup.params['usb_info']['bulk']['bus'], idVendor=platform_setup.params['usb_info']['bulk']['idVendor'], idProduct=platform_setup.params['usb_info']['bulk']['idProduct'])
   
if power_controller:
    power_controller.switch_off()
else:
    print 'Release reset button now....'
    
platform.expect('CCC',10)
if not serial_load('bootloader/Release/boot.bin'):
    raise Exception('Unable to load bootloader into platform')
platform.expect('CCC')


#Loading USB-DEV-BULK application
usb_bin = 'usb_dev_bulk/Release/usb_dev_bulk.bin'
if not serial_load(usb_bin):
    raise Exception('Unable to load test binary ' + usb_bin) 
    
#This is the buffer size defined in the usb_dev_bulk example
bulk_buffer_size=255

try:
    
    #Getting a USB handle of the device to be tested.
    #Unfortunately the device gets assigned a new USB address every time it is rebooted, 
    #and all platforms for the same SoC have the same Vendor ID and product ID so
    #it has to be found by the difference betweem preboot and post boot information.
    #Even then there is chance that if two instances of STP are running this testcase
    #or a test case with this functionality at the same time, then the device detected 
    #might be the wrong device.
    for i in range(1,5):
        # find our device
        dev_list = usb.core.find(find_all=True, bus=platform_setup.params['usb_info']['bulk']['bus'], idVendor=platform_setup.params['usb_info']['bulk']['idVendor'], idProduct=platform_setup.params['usb_info']['bulk']['idProduct'])

        # was it found?
        if len(dev_list) > len(preboot_usb_list):
            break
        else:
            time.sleep(4)
    else:
        raise Exception('USB Device not found')
    
    dev = None
    preboot_addresses = set([ preboot_dev.address for preboot_dev in preboot_usb_list])
    current_addresses = set([ current_dev.address for current_dev in dev_list])
    dev_address = (current_addresses - preboot_addresses).pop()
    dev = usb.core.find(address=dev_address, bus=platform_setup.params['usb_info']['bulk']['bus'], idVendor=platform_setup.params['usb_info']['bulk']['idVendor'], idProduct=platform_setup.params['usb_info']['bulk']['idProduct'])
    
    print 'Found device with following usb info:'
    print 'Bus: ', dev.bus
    print 'Address: ', dev.address
    print 'Vendor Id: ', dev.idVendor
    print 'Product Id: ', dev.idProduct
    
    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()

    # get an endpoint instance
    cfg = dev.get_active_configuration()
except Exception, e:
    print "%r"%e , ('Before running this test: 1) Make sure the device has been installed successfully.' +
        '2)The usb_info property exists in the bench and contains all the necessary fields, ' +
        ' \'bulk\':{\'bus\':<bus id>, \'idVendor\':<usb vendor id>, \'idProduct\':<usb product id>}, for the board.' +
        '3)For Linux systems also make sure there is a rule with the appropriate mode, i.e ' + 
        '\'SUBSYSTEM=="usb", ATTR{idVendor}=="%04x", ATTR{idProduct}=="%04x", MODE="666"\', ' +
        "in one of the files located at /etc/udev/rules.d/")%(platform_setup.params['usb_info']['bulk']['idVendor'],platform_setup.params['usb_info']['bulk']['idProduct'])
    raise e

# cfg index is a tuple of two values with interface index and
# alternate setting index.
interface_number = cfg[(0,0)].bInterfaceNumber

alternate_setting = usb.control.get_interface(dev,interface_number)

intf = usb.util.find_descriptor(
    cfg, bInterfaceNumber = interface_number,
    bAlternateSetting = alternate_setting
)

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT
)

ep2 = usb.util.find_descriptor(
    intf,
    # match the first IN endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_IN
)

if ep == None:
    raise 'Unable to find OUT endpoint in device'
    
if ep2 == None:
    raise 'Unable to find IN endpoint in device'

test_string = string.letters*50

received_string = ''

# write the data
print 'Sending test string of length %d...'%len(test_string)

for substring in re.findall('.{1,%d}'%bulk_buffer_size, test_string):
    ep.write(substring)
    # read data
    for letter in ep2.read(len(substring)):
        received_string+= chr(letter)

print 'Received string of length ', len(received_string)

if test_string == received_string.swapcase():
    testresult = {'RC':'P', 'Comments':'Received string matched sent string with letters case swapped','Perf':None}
else:
    testresult = {'RC':'F', 'Comments':'Received string did not match sent string with letters case swapped','Perf':None}
