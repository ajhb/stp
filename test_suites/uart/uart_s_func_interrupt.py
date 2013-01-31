#@desc Uart-interrupt example test. Verifies basic UART functionality on the board.
#Currently only verifies UART on evmskAM335x
requires = ['uart', 'evmskAM335x']

import re
import pexpect
import time

def get_menu_string(selection=None, expected_string = None):
    if selection:
        platform.write(selection)
    if expected_string:
        platform.expect(expected_string)
    else:
        platform.expect('Enter\s*the\s*serial\s*number\s*of\s*your\s*choice:',10)
#   print platform.before
#   print platform.after
    return platform.before

#The next two function convert from ascii to hex value and vice versa. The functions are not generic
# they are specific to the character set [asdfegHI]
def convert_tststring_to_5o6bit(tstring):
    lookup_table = {
        'a': chr(0x03),
        's': chr(0x05),
        'd': chr(0x09),
        'f': chr(0x0d),
        'e': chr(0x01),
        'g': chr(0x1a),
        'H': chr(0x14),
        'I': chr(0x06)
    }
    result = ''
    for letter in tstring:
        result += lookup_table.get(letter,letter)
            
    return result
    

def convert_5o6_bit_to_estring(estring):
    lookup_table = {
        0x03:'a',
        0x05:'s',
        0x09:'d',
        0x0d:'f', 
        0x01:'e',
        0x1a:'g',
        0x14:'H',
        0x06:'I'
    }
    result = ''
    for tst in [ item[0]+item[1] for item in zip(estring[0::2],estring[1::2])]:
        letter = int(tst,16)
        result += lookup_table.get(letter,letter)
    
    return result
        
def load_uart_app():
    #Importing common code for loading bootloader
    runstp_import('test_suites/templates/load_template.py')

    #Loading UART-interrupt application
    uart_bin = 'uart/Release/uartEcho.bin'
    if not serial_load(uart_bin):
        raise Exception('Unable to load test binary ' + uart_bin) 


#Definition of contraints arrays
data_bits_7_8_platforms =  ['evmskAM335x','beaglebone']

#Start of test logic
load_uart_app()

#Defining the test strings
test_string = 'asdfegHI'

#Going through initial run in the app
platform.expect('Please enter 8 bytes. They will echoed back individually.')
platform.send(test_string)
platform.expect(test_string)

#Parsing all possible test option
main_options_string = get_menu_string()
main_option_default_settings = re.findall('\d+(?=.*?Default\s*Settings)', main_options_string, re.I)
main_option_change_settings = re.findall('\d+(?=.*?Baud\s*Rate)', main_options_string, re.I)
main_option_exit = re.findall('\d+(?=.*?exit)', main_options_string, re.I)

baud_rates_string = get_menu_string(main_option_change_settings[0])

baud_rates_info = re.findall('(\d+)>\s*(\d+)\s*bps', baud_rates_string, re.I)

data_bits_string = get_menu_string('\r')
data_bits_info = re.findall('(\d+)>\s*(\d+)\s*bit', data_bits_string, re.I)
stop_bits_string = get_menu_string('\r')
stop_bits_info = re.findall('(\d+)>\s*([\d\.]+)\s*stop\s*bit.*?([\d,\s]+(?=\)))+', stop_bits_string, re.I)

parity_string = get_menu_string('\r')
parity_info = re.findall('(\d+)>(?:.*?(forced\s*to\s*\d)|(?:.*?(\w+)\s*parity)).*?', parity_string, re.I)

platform.send('\r')
platform.expect('Please enter 8 bytes. They will echoed back individually.')
platform.send(test_string)
platform.expect(test_string)

print 'Host capabilities:'
print serial_connection.BAUDRATES
print serial_connection.BYTESIZES
print serial_connection.PARITIES
print serial_connection.STOPBITS

default_serial_params = serial_connection.getSettingsDict()

testresult = []
try:
    test_comment = ''
    current_config = None
    #Testing all possible configurations
    
    #Baud rate loop
    for baud_rate in baud_rates_info:
        #Bypassing modes that are not applicable to a platform or UART operational mode
        if ((platform_info.platform == 'evmAM335x' or 'edma' not in requires) and int(baud_rate[1]) > 115200) or int(baud_rate[1]) not in serial_connection.BAUDRATES:
            continue
        #Data bits loop
        for data_bits in data_bits_info:
            #Continue on data bits not 7 or 8 for platforms that do not support 5 and 6 data bits
            if  (platform_info.platform in data_bits_7_8_platforms and data_bits[1] not in ['7','8']) or int(data_bits[1]) not in serial_connection.BYTESIZES: 
                continue
            #Stop bits loop
            for stop_bits in stop_bits_info:
                valid_data_bits = re.split('[\s,]+',stop_bits[2])
                if data_bits[1] not in valid_data_bits:
                        continue
                #Parity loop       
                for parity in parity_info:
                    #Continue on MARK or SPACE parity since pyserial throws error when trying to set to these parities
                    if re.search('forced\s*to\s*[10]',parity[1], re.I):
                        continue
                    
                    #Reconfiguring dut UART
                    print "\r\n\r\nTesting with following UART settings:"
                    platform.expect('Enter\s*the\s*serial\s*number\s*of\s*your\s*choice:',10)
                    get_menu_string(main_option_change_settings[0])
                    print "Baud rate = " + baud_rate[1]
                    get_menu_string(baud_rate[0], 'Baud Rate selected = ' + baud_rate[1] + ' bps.')
                    print "Data bits = " + data_bits[1]
                    get_menu_string(data_bits[0], 'Selected Word Length per frame = ' + data_bits[1])
                    print "Stop bits = " + stop_bits[1]
                    get_menu_string(stop_bits[0], 'Selected Number of Stop Bits per frame = ' + stop_bits[1])
                    print "Parity = " + parity[1] + parity[2]
                    get_menu_string(parity[0],'Selected Parity Configuration = ' + parity[1].replace('forced to','Parity bit is') + parity[2])
                    current_config = baud_rate[1] + '-' + data_bits[1] + '-' + parity[1] + parity[2] + '-' + stop_bits[1] 
                    
                    #Reconfiguring host UART
                    serial_connection.baudrate = int(baud_rate[1])
                    if data_bits[1] == '5':
                        serial_connection.bytesize = serial.FIVEBITS
                    elif data_bits[1] == '6':
                        serial_connection.bytesize = serial.SIXBITS
                    elif data_bits[1] == '7':
                        serial_connection.bytesize = serial.SEVENBITS
                    elif data_bits[1] == '8':
                        serial_connection.bytesize = serial.EIGHTBITS
                    
                    if parity[2].lower() == 'no':
                        serial_connection.parity = serial.PARITY_NONE
                    elif parity[2].lower() == 'even':
                        serial_connection.parity = serial.PARITY_EVEN
                    elif parity[2].lower() == 'odd':
                        serial_connection.parity = serial.PARITY_ODD
                    elif parity[1].lower() == 'forced to 1':
                        serial_connection.parity = serial.PARITY_MARK
                    elif parity[1].lower() == 'forced to 0':
                        serial_connection.parity = serial.PARITY_SPACE
                    
                    if stop_bits[1] == '1':
                        serial_connection.stopbits = serial.STOPBITS_ONE
                    elif stop_bits[1] == '1.5':
                        serial_connection.stopbits = serial.STOPBITS_ONE_POINT_FIVE
                    elif stop_bits[1] == '1.5':
                        serial_connection.stopbits = serial.STOPBITS_TWO
                        
                    time.sleep(1) #wait 1 sec for changes to take effect
                    
                    #Running 8 character test
                    platform.expect(['Please\s*enter\s*8\s*bytes', pexpect.TIMEOUT],10)
                        
                    #Sending 1 letter at a time to mimic keyboard input
                    #If using 5 or 6 data bits then send hex value
                    if data_bits[1] in ['5','6']:
                        for letter in convert_tststring_to_5o6bit(test_string):
                            time.sleep(float(9*len(test_string)/float(baud_rate[1])))
                            serial_connection.write(letter)
                    else:
                        for letter in test_string:
                            time.sleep(float(9*len(test_string)/float(baud_rate[1])))
                            serial_connection.write(letter)
                                                
                    #Verifying the string echoed by the board
                    #If using 5 or 6 data bits than do a hex check, othewise, check for test_string
                    if data_bits[1] in ['5','6']:
                        echoed_string = serial_connection.read(8)
                        if convert_5o6_bit_to_estring(echoed_string.encode('hex')) == test_string:
                            idx = 1
                        else:
                            idx = 2
                    else:
                        idx = platform.expect([test_string, pexpect.TIMEOUT],5)
                    
                    if idx:
                        if data_bits[1] not in ['5','6'] or idx ==2:
                            testresult.append({'RC': 'F', 'Comments': current_config + ' FAILED', 'Perf': None})
                            print "TEST FAILED"
                        else:
                            testresult.append({'RC': 'P', 'Comments': current_config + ' PASSED', 'Perf': None})
                            print "TEST PASSED"
                        serial_connection.applySettingsDict(default_serial_params)
                        time.sleep(1) #wait 1 sec for changes to take effect
                        load_uart_app()
                        platform.send(test_string)
                        platform.expect(test_string)
                    else:
                        print "TEST PASSED"
                        testresult.append({'RC': 'P', 'Comments': current_config + ' PASSED', 'Perf': None})
            
except Exception,e: 
    print traceback.format_exc()
    testresult.insert(0,{'RC': 'F', 'Comments': current_config + ' FAILED and set UART in unrecoverable test state. ' +  "%r"%e , 'Perf': None})

#Resetting serial connection to original settings
serial_connection.applySettingsDict(default_serial_params)

               
