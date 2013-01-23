#@desc Just hello world with binary loaded to target

# What's required to run this test
requires = []


# START OF TEST LOGIC
print 'Reboot or power cycle the board now....'
print serial_load('bootloader/Release/boot.bin')
platform.expect('CCC')
print serial_load('hello_world/Release/hello_world.bin')
platform.expect('Hello World!!!! from Starterware')

# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
testresult = {'RC': 'P', 'Comments': "YOOOOOOOHOOOOOOOOOOOOO!!!!!!!!!!!!!", 'Perf': None}