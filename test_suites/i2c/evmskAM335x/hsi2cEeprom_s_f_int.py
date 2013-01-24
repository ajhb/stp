# The script executes hsi2cEeprom test application.
# The script enters user input interactivley and verify the test result automatically.

#list of all requirments  
requires = ['evmskAM335x','i2c','uart']
#user input number of bytes to be read 
number_of_bytes_to_read = '500'
#user input eeprom location to be read 
address_to_read_from = '00'
#user input i2c frequency configuration 
i2c_frequency = '300'
test_status = ''
#load the boot file 
runstp_import('test_suites/templates/load_template.py')
#load test application binary file located on starterware binary directory.  
if (serial_load('hsi2c_eeprom/Release/hsi2cEeprom.bin') == 1): 
    platform.expect('Enter\s+the\s+bus\s+frequency',timeout=10)
    platform.send(i2c_frequency + '\r')
    platform.expect('Enter\s+an\s+address\s+in\s+EEPROM\s+starting\s+from\s+which',timeout=10)
    platform.send(address_to_read_from + '\r')
    platform.expect('Enter\s+the\s+number\s+of\s+data\s+bytes\s+to\s+be\s+read',timeout=10)
    platform.send(number_of_bytes_to_read + '\r')
    platform.expect('Data\s+read\s+from\s+EEPROM:',timeout=10)
    data_to_check = int(number_of_bytes_to_read) - 1
    #test data is detected or verified by expect.  
    index = platform.expect('([A-Z0-9][A-Z0-9],){' + str(data_to_check) + '}')
    if index == 0:
        test_status = "P"
        print "TEST PASS"
    else: 
        test_status = "F"
        print "TEST FAIL"
else:
    test_status = "F"
    print "hsi2cEeprom.bin loading failed.\n"
# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
testresult = {'RC': test_status, 'Comments': "EePROM READ SUCCESS", 'Perf': None}
