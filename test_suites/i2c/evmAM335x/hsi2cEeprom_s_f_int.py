# The script executes hsi2cEeprom test application.
# The script enters user input interactivley and verify the test result automatically.

#list of all requirments  
requires = ['evmAM335x','i2c','uart']
#Hardcoded in the test application 
number_of_bytes_to_read = 50
#user input i2c frequency configuration
i2c_frequency = '300'
test_status = ''
#load the boot file 
runstp_import('test_suites/templates/load_template.py')
#load test application binary file located on starterware binary directory.  
if (serial_load('hsi2c_eeprom/Release/hsi2cEeprom.bin') == 1):
    platform.expect('Enter\s+the\s+bus\s+frequency',timeout=100)
    platform.send(i2c_frequency + '\r')
    platform.expect('Data\s+read\s+from\s+EEPROM:',timeout=100)
    #test data is detected or verified by expect   
    index = platform.expect('([A-Z0-9][A-Z0-9],){' + str(number_of_bytes_to_read -1) + '}')
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
