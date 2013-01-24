#@desc Just hello world with binary loaded to target

# What's required to run this test, this line should always be the first statement in every python test script
requires = []


# START OF TEST LOGIC

# Telling user to reboot/reset the board before starting
print 'Reboot or power cycle the board now....'

# Loading the bootloader into the board. See README file for information regarding serial_load function
serial_load('bootloader/Release/boot.bin')

# Waiting for the CCC sequence, which signals that the board is ready to receive the binary
platform.expect('CCC')

# Loading the test binary into the board
serial_load('hello_world/Release/hello_world.bin')

# Waiting for the expected output
platform.expect('Hello World!!!! from Starterware')

# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
testresult = {'RC': 'P', 'Comments': "YOOOOOOOHOOOOOOOOOOOOO!!!!!!!!!!!!!", 'Perf': None}