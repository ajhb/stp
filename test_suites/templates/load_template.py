
# START OF TEST LOGIC
if power_controller:
    power_controller.reset()
else:
    print 'Reboot or power cycle the board now....'

platform.expect('CCC',10)
if not serial_load('bootloader/Release/boot.bin'):
    raise Exception('Unable to load bootloader into platform')
platform.expect('CCC')
