# @desc USB-DEV-MSC example test. Verifies basic msc functionality on the device.
# Before running this test Make sure the device has been installed successfully. 
# For Linux systems also make sure there is a rule with the appropriate mode 
# (SUBSYSTEM=="usb", ATTR{idVendor}=="<your Vendor ID>", ATTR{idProduct}=="<your product ID>", MODE="666")
# in one of the files located at /etc/udev/rules.d/

requires = ['usb']

import glob
import string
import re
import time
import pexpect
import subprocess
import stat

# START OF TEST LOGIC
if power_controller:
    power_controller.switch_on()
else:
    print 'Press and hold reset button now....'

time.sleep(3)
preboot_usb_list = glob.glob(platform_setup.params['usb_info']['msc'])
   
if power_controller:
    power_controller.switch_off()
else:
    print 'Release reset button now....'

platform.expect('CCC',10)
if not serial_load('bootloader/Release/boot.bin'):
    raise Exception('Unable to load bootloader into platform')
platform.expect('CCC')


#Loading USB-DEV-BULK application
usb_bin = 'usb_dev_msc/Release/usb_dev_msc.bin'
if not serial_load(usb_bin):
    raise Exception('Unable to load test binary ' + usb_bin) 
    
try:
    # Getting the dev node of the device to be tested.
    # has to be found by the difference betweem preboot and post boot information
    for i in range(1,5):
        # find our device
        dev_list = glob.glob(platform_setup.params['usb_info']['msc'])

        # was it found?
        if len(dev_list) > len(preboot_usb_list):
            break
        else:
            time.sleep(4)
    else:
        raise Exception('USB Device not found')

    dev = (set(dev_list) - set(preboot_usb_list)).pop()

    print 'Found MSC device with following dev node: ', dev
except Exception,e:
    print "%r"%e , ('Before running this test: 1) Make sure the device has been installed successfully.' +
        '2)The usb_info property exists in the bench and contains all the necessary fields, ' +
        ' {\'msc\':\'<dev drive or node>\'}, for the board.' +
        '3)For Linux systems also make sure there is a rule with the appropriate mode, i.e ' + 
        '\'SUBSYSTEM=="usb", ATTR{idVendor}=="<idVendor>", ATTR{idProduct}=="<idProduct>", MODE="666"\', ' +
        "in one of the files located at /etc/udev/rules.d/")
    raise e

usb_log=open(get_log_path('usb_dev_msc.log'),'a+')

# Checking the host machine has the appropriate OS
if sys.platform.find('linux') > -1:
    #Function to run commands a sudo
    def send_sudo_cmd(cmd):
        sudo_proc = pexpect.spawn(cmd)
        sudo_proc.logfile=usb_log
        pass_idx = sudo_proc.expect([pexpect.TIMEOUT, 'password for.*?:'],3)
        if pass_idx:
            sudo_proc.sendline(platform_setup.params['host'].params['password'])
        
        return sudo_proc
        
    #Partitioning the MSC device
    fdisk_proc = send_sudo_cmd('sudo fdisk ' + dev)
    fdisk_proc.expect('Command\s*\(m\s*for\s*help\):',3)
    fdisk_proc.sendline('n')
    fdisk_proc.expect('Select\s*\(default\s*p\):',3)
    fdisk_proc.sendline('p')
    fdisk_proc.expect('Partition\s*number\s*\(1-4,\s*default\s*1\):',3)
    fdisk_proc.sendline('1')
    fdisk_proc.expect('First\s*sector\s*\(\d+-\d+,\s*default\s*\d+\):',3)
    fdisk_proc.sendline('')
    fdisk_proc.expect('Last\s*sector,\s*\+sectors\s*or\s*\+size\{K,M,G\}\s*\(\d+-\d+,\s*default\s*\d+\):',3)
    fdisk_proc.sendline('')
    fdisk_proc.expect('Command\s*\(m\s*for\s*help\):',3)
    fdisk_proc.sendline('t')
    fdisk_proc.expect('Hex\s*code\s*\(type\s*L\s*to\s*list\s*codes\):')
    fdisk_proc.sendline('c')
    fdisk_proc.expect('Command\s*\(m\s*for\s*help\):',3)
    fdisk_proc.sendline('w')
    fdisk_proc.expect('Syncing\s*disks.',3)
    
    #Formating / Creating file system in the partition
    dev_partition = dev + '1'
    mkfs_proc = send_sudo_cmd('sudo mkfs -t vfat ' + dev_partition) 
    mkfs_proc.expect('mkfs.vfat')
    time.sleep(1)
    
    #Obtaining the device's mount point
    mount_string = subprocess.check_output('mount')
    mount_point = re.search('(?<='+dev_partition + ')\s*on\s*(.+?)\s*type.*',mount_string,re.I).group(1)
else:
    usb_log.close()
    raise Exception('Test does not support host\'s OS')
usb_log.close()
testresult = []
print 'Device mounted on: ',  mount_point

#Defining file and directory paths for the test
msc_test_dir = os.path.join(mount_point,'usb_dev_msc_test')
msc_test_file = os.path.join(msc_test_dir,'usb_test_file.txt')

#Testing make dir
os.makedirs(msc_test_dir)
testresult.append({'RC':'P', 'Comments':'Make dirs passed', 'Perf':None})
msc_file = open(msc_test_file,'w+')
msc_test_string = 'This is the usb device msc test string'
msc_file.write(msc_test_string)
msc_file.close()

#Testing file creation
msc_file = open(msc_test_file,'r')
test_comment = ''
if msc_file.readline() == msc_test_string:
    testresult.append({'RC':'P', 'Comments':'File R/W passed', 'Perf':None})
else:
    testresult.append({'RC':'F', 'Comments':'File R/W failed', 'Perf':None})
msc_file.close()

#Testing mode functionality
os.chmod(msc_test_file,stat.S_IREAD)
try: 
    msc_file = open(msc_test_file,'w')
    msc_file.write('Should not be able to write this')
    msc_file.close()
    testresult.append({'RC':'F', 'Comments':"File chmod failed, was able to open file for writing after setting mode to read only", 'Perf':None})
except IOError:
    testresult.append({'RC':'P', 'Comments':'File chmod passed', 'Perf':None})
except Exception, e:
    testresult.append({'RC':'F', 'Comments':"%r"%e, 'Perf':None})
os.chmod(msc_test_file,stat.S_IREAD|stat.S_IWRITE)

#Testing file deletion
os.remove(msc_test_file)
if not os.path.exists(msc_test_file):
    testresult.append({'RC':'P', 'Comments':'Delete file passed', 'Perf':None})
else:
    testresult.append({'RC':'F', 'Comments':'Delete file failed, file not removed', 'Perf':None})

#Testing directory deletion
os.rmdir(msc_test_dir)
if not os.path.exists(msc_test_dir):
    testresult.append({'RC':'P', 'Comments':'Delete dir passed', 'Perf':None})
else:
    testresult.append({'RC':'F', 'Comments':'Delete dir failed, dir not removed', 'Perf':None})