# The script executes hsi2cEeprom_edma test application.
# The script enters user input interactivley and verify the test result automatically.

#list of all requirments  
requires = [['beaglebone','evmAM335x'],'i2c','uart','edma']
#Hardcoded in the test application 
number_of_bytes_to_read = 50
test_status = ""
#load the boot file
runstp_import('test_suites/templates/load_template.py')
if (serial_load('hsi2c_eeprom_edma/Release/hsi2cEeprom_edma.bin') == 1):
    #test data is detected or verified by expect   
    index = platform.expect('([A-Z0-9][A-Z0-9],){' + str(number_of_bytes_to_read - 1) + '}')
    if index == 0:
        test_status = "P"
        test_comment = "TEST PASS"
    else: 
        test_status = "F"
        test_comment = "TEST FAIL"
else:
    test_status = "E"
    test_comment = "hsi2cEeprom_edma.bin loading failed"
# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
print test_comment 
testresult = {'RC': test_status, 'Comments': test_comment, 'Perf': None}


