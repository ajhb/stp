
# START OF TEST LOGIC
print 'Reboot or power cycle the board now....'
serial_load('bootloader/Release/boot.bin')
platform.expect('CCC')
