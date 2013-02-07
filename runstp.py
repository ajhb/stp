#!/usr/bin/python

import os
import sys
import types
import imp
import serial
import fdpexpect
import traceback
import xmodem
import logging
import re

from src.test_equipment.test_equipment import *

from time import gmtime, strftime
from optparse import OptionParser

#Setting default logging configuration for modules that use python's logging module
logging.basicConfig()
logging.level=logging.DEBUG

#Defining some runstp constants and variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) #runstp root folder. Folder where runstp is located
TEST_SUITES_DIR = os.path.join(ROOT_DIR, 'test_suites') #runstp test suites directory. Folder where runstp test suites are located relative to ROOT_DIR
PLATFORMS_DIR = os.path.join(ROOT_DIR, 'platforms') #runstp platform info directory. Folder where runstp keeps files containing information related to the platforms like architecture, interfaces, etc
TEST_BIN_ROOT = os.path.join(ROOT_DIR, '..','..','binary') #compiled test binaries location
LOGS_ROOT_DIR = os.path.join(ROOT_DIR,'logs') #logs root folder

#Function to parse comma separated arguments
def runstp_parser(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

#Function to obtain possible test case candidates from the existing test cases
def get_test_case_candidates(root_folder, test_cases=None):
    result = []
    for folder in root_folder:
        for root, dirs, files in os.walk(folder):
           if root.find(os.path.join(TEST_SUITES_DIR,'templates')) != 0:
                for item in files:
                    if test_cases:
                        for test_spec in test_cases:
                            if re.search(test_spec,item,re.I):
                                result.append(os.path.join(root,item))
                    elif item.endswith('.py'):
                        result.append(os.path.join(root, item))
    
    return result

# Function to import templates in test cases with access to runstp objects within the module. Python built-in import can not be used since modules are imported 
# in their one environment and runstp objects like platform will not be recognized by the imported module.
# Takes:
#       - module_path a string containing the path to the code to be imported relative to <stp install folder>
#       - glob (Optional) A dictionary containing global environment definitions. Useful if you want the imported module to modify global variables/objects
#       - loc (Optional) A dictionary containing local environment definitions. Useful if you want the imported module to modify local variables/objects
def runstp_import(module_path, glob=None, loc=None):
    exec(compile(open(os.path.join(ROOT_DIR,module_path)).read(), os.path.join(ROOT_DIR,module_path), 'exec'),glob,loc)
    
# Function to print info message and exit
def print_message_and_exit(message):
    print (message)
    sys.exit(1)

# Function to check if the platform being used supports the required interfaces specified by the requires value in the test case
def check_requires_field(requires, platform_features):
    for item in requires:
        if isinstance(item,list):
            if not set(item) & set(platform_features):
                return False
        elif item not in set(platform_features):
            return False
    return True
    
#Defining the command line options for runstp
parser = OptionParser()

#Options to pass folder (test suites)
parser.add_option("-f", "--folders", 
          dest="folders", action="callback", callback=runstp_parser, type="string",
                  help="Execute runstp testsuites (comma separated)", metavar="FILE")
#Option to pass test cases
parser.add_option("-t", "--testcases",
                  action="callback", callback=runstp_parser, dest="testcases", type="string",
                  help="Execute runstp testcases name patterns (comma separated)")
#Option to pass platform
parser.add_option("-p", "--platform",
                  action="store", dest="platform", type="string",
                  help="Platform being used in the tests (mandatory)")
#Option to pass bench file
parser.add_option("-b", "--bench",
                  action="store", dest="bench_path", type="string", default=os.path.join(ROOT_DIR,'bench.py'),
                  help="File containing equipment connectivity and setup info (defaults to <runstp folder>/bench.py)")

#Option to pass bench file
parser.add_option("-c", "--compiler",
                  action="store", dest="compiler", type="string", default='gcc',
                  help="Compiler user to generate test case binaries (gcc,cgt_ccs,etc)")
          

#Parsing commad line arguments
(options, args) = parser.parse_args()

if not options.platform:
    print "Plaform -p/--plaform is mandatory"
    parser.print_help()
    sys.exit(1)
    
test_case_candidates = [] #test case candidates set
test_suite_candidates = [] #test suite candidates set

#Setting the folder to be searched for test case candidates
if options.folders:
    for folder in options.folders:
        test_suite_candidates.append(os.path.join(TEST_SUITES_DIR,folder))
else:	
    test_suite_candidates = [TEST_SUITES_DIR]

#Obtaining the test cases candidates if no options are passed or if -f is passed in the command line
if  not options.testcases or options.folders:
    test_case_candidates.extend(get_test_case_candidates(test_suite_candidates))

#Obtaining the test cases candidates if -t is passed in the command line
if options.testcases:
    test_case_candidates.extend(get_test_case_candidates([TEST_SUITES_DIR], options.testcases))

#Eliminating duplicate test cases from the list of candidates
test_case_candidates = set(test_case_candidates)

#Obtaining the platform specific information
try:
    platform_info = imp.load_source(options.platform,os.path.join(PLATFORMS_DIR, options.platform + '.py'))
    platform_features = []
    for item_string in dir(platform_info):
        if item_string not in ['__builtins__', '__doc__', '__file__', '__name__', '__package__']:
            item = getattr(platform_info, item_string)
            if isinstance(item,list):
                platform_features.extend(item)
            elif isinstance(item,dict):
                platform_features.extend(item.keys())
            else:
                platform_features.append(item)
except Exception, e:
    print e
    print_message_and_exit ('Problem occurred while trying to obtain platform information for ' + options.platform +
                                          '. Make sure that a ' + options.platform + '.py file exists in ' + PLATFORMS_DIR + 
                                          ' and that no errors are present in the file.')

#Obtaining the physical setup of the board
from src.equipment_info import *

try:
    exec(compile(open(options.bench_path).read(), options.bench_path, 'exec'), None, None)
except:
    print traceback.format_exc()
    print_message_and_exit ('Problem occurred while trying to parse ' + options.bench_path +
               '. Make sure that ' + options.bench_path + ' exists and that no errors are present in the file.\n' + 
               ' First time users can use ' + os.path.join(ROOT_DIR,'default_bench.py') + ' as a starting point to create the file.\n' +
               ' Option -b can be used to point to a different location for the file.\n')

#Verifying that ther is an entry for the platform in the bench file specified
if not platforms_list.has_key(options.platform):
    print_message_and_exit ('No entry found for ' + options.platform + ' in ' + options.bench_path)

# Creating path to root directory of test binaries
test_bins_root = os.path.join(TEST_BIN_ROOT, platform_info.arch, options.compiler, platform_info.soc, platform_info.platform)

def load_getc(size, timeout=1):
    return serial_connection.read(size)

def load_putc(data, timeout=1):
    return serial_connection.write(data)
    
# Function to load application into platform
def serial_load(bin_path, root_path=test_bins_root):
    modem = xmodem.XMODEM(load_getc, load_putc)
    stream = open(os.path.join(test_bins_root,bin_path), 'rb')
    result = modem.send(stream)
    stream.close()
    return result
     
#Running the appropriate test cases
test_results = {} #Results Dictionary

test_case_defs = os.path.join(TEST_SUITES_DIR,'templates','test_defaults.py')
exec(compile(open(test_case_defs).read(),test_case_defs, 'exec'),None,None)  #Importing the test case default values

serial_params = platforms_list[options.platform].init_info
session_start_time = strftime("%a_%d_%b_%Y_%H.%M.%S", gmtime())

#Function to create instances of drivers associated with an equipment     
def get_equipment(equipment_info):
    try:
        if equipment_info.init_info:
            equipment = getattr(sys.modules[__name__],equipment_info.driver_class_name)(equipment_info.init_info)
        else:
            equipment = getattr(sys.modules[__name__],equipment_info.driver_class_name)()
        
        if equipment_info.params:
            for param_name, param_value in equipment_info.params.iteritems():
                setattr(equipment, param_name, param_value)
                
        return equipment
    except Exception, e:
        print traceback.format_exc()
        raise Exception('Problem while trying to Initialize Equipment ' + equipment_info.name + ', ' + str(equipment_info.buildId) +
        '. Please check information in your bench for this equipment\n'+"%r"%e)
        
#Creating the power controller for the platform if power_port has been specified in bench.py
power_controller = None

try:
    if platforms_list[options.platform].params and 'power_port' in platforms_list[options.platform].params:
        for power_info, power_port in platforms_list[options.platform].params['power_port'].iteritems():
            power_controller=getattr(sys.modules[__name__],power_info.driver_class_name)(power_info.init_info)
            power_controller.power_port = power_port
except Exception, e:
    print ('Problem while trying to Initialize power controller for ' + platforms_list[options.platform].name + '-' + str(platforms_list[options.platform].buildId) + 
    ', please check power_port information for the board')
    print e
    print traceback.format_exc()
    sys.exit(0)

serial_connection = None
platform_setup = platforms_list[options.platform]
__clean_attr__ = set(dir())
dirty_attr = set(dir())
for testcase in test_case_candidates:
    try:
        requires = None
        exec(compile(open(testcase).read(), testcase, 'single'),None,None)
        if check_requires_field(requires, platform_features):
            
            #Cleaning environment before running the test case
            for new_attr in dirty_attr - __clean_attr__:
                if new_attr in ['__clean_attr__','testcase']:
                    continue
                delattr(sys.modules[__name__], new_attr)
            
            #Creating logs folder and log file
            test_case_log_folder = os.path.join(LOGS_ROOT_DIR,platform_info.arch,options.compiler,platform_info.soc,platform_info.platform,session_start_time) + testcase.replace(TEST_SUITES_DIR,'').replace('.py','')
            os.makedirs(test_case_log_folder)
            
            #Function to return log folder location for test case
            #file_name : string containing the name of the log file
            #Returns: complete path of the log file if file_name is given, otherwise, returns the logs folder path
            def get_log_path(file_name=None):
                if file_name:
                    return os.path.join(test_case_log_folder, file_name)
                return test_case_log_folder
                
            test_log_file = open(os.path.join(test_case_log_folder, platforms_list[options.platform].name + '_' + str(platforms_list[options.platform].buildId) + '.log'), 'a+')
            #Initializing common vairables
            testresult = {'RC':'f', 'Comments':"Default testresult value, please overwrite testresult in your test script ", 'Perf': None}
            print 'Running ' + testcase + ' at ' + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            #'port':'/dev/ttyUSB8', 'baudrate':19200, 'bytesize':8, 'parity':'N', 'stopbits':1, 'timeout':None, 'xonxoff':0, 'rtscts':0
            serial_connection = serial.Serial(serial_params['port'])
            if serial_params['baudrate']:
                serial_connection.baudrate = serial_params['baudrate']
            if serial_params['bytesize']:
                serial_connection.bytesize = serial_params['bytesize']
            if serial_params['parity']:
                serial_connection.parity = serial_params['parity']
            if serial_params['stopbits']:
                serial_connection.stopbits = serial_params['stopbits']
            if serial_params['timeout']:
                serial_connection.timeout = serial_params['timeout']
            if serial_params['xonxoff']:
                serial_connection.xonxoff = serial_params['xonxoff']
            if serial_params['rtscts']:
                serial_connection.rtscts = serial_params['rtscts']
            platform = fdpexpect.fdspawn(serial_connection)
            platform.logfile = test_log_file
            exec(compile(open(testcase).read(), testcase, 'exec'),None,None)
            test_results[testcase.replace(TEST_SUITES_DIR,'')] = testresult 
            test_log_file.close
        else: 
            print 'Test ' + testcase + ' can not be run because platform ' + options.platform + ' does not have required interfaces '
    except Exception, e:
        print traceback.format_exc()
        test_results[testcase.replace(TEST_SUITES_DIR,'')]  = {'RC': 'F', 'Comments': e, 'Perf': None} 
    if serial_connection:
        serial_connection.close()
    dirty_attr = set(dir())    
print "\n\nResults summary"
for key, val in test_results.items():
    sys.stdout.write(key)
    sys.stdout.write('     ')
    sys.stdout.write("%r"%val)
    print('')
     
print '\n\nLogs for this session can be found at file://'+os.path.join(LOGS_ROOT_DIR,platform_info.arch,options.compiler,platform_info.soc,platform_info.platform,session_start_time) 
