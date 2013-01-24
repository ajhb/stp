#@desc Just hello world with template importing. This test case showcases loading reusable/common
# code into a test case to avoid code duplication.
#

# What's required to run this test, this line should always be the first statement in every python test script
requires = []

# START OF TEST LOGIC

# Importing load_template.py template that takes care of loading the bootloader into the board
runstp_import('test_suites/templates/load_template.py')

# Loading the test binary into the board
serial_load('hello_world/Release/hello_world.bin')

# Waiting for the expected output
platform.expect('Hello World!!!! from Starterware')

# Return test Result. Valid RC: 'p' => passed, 'f' => failed, 'e' => error
# Perf is an optional hash with performance data {'name': "testname", 'values': [], 'units': "values unit"}
testresult = {'RC': 'P', 'Comments': "YOOOOOOOHOOOOOOOOOOOOO!!!!!!!!!!!!!", 'Perf': None}