
# START OF TEST LOGIC
print 'Reboot or power cycle the board now....'
if not serial_load('bootloader/Release/boot.bin'):
    raise Exception('Unable to load bootloader into platform')
platform.expect('CCC')
