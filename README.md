stp

Starterware Test Project

================================================================================

1) GOALS:
================================================================================
 * Validate the functionality, performance and stability of Starterware drivers
 * Validate performance and stability of the whole system running starterware based applications.
 * Maximize use of open source software and contribute to improve it.
 * Maximize code reuse across different platforms.
 * Make it easy to support new embedded platforms.

2) ARCHITECTURE HIGHLIGHTS:
================================================================================
 * Support dynamic selection/filtering of test cases based on platform
 * Based on ptyhon, so the full python API is available when wiriting test scripts
 
3) DIRECTORY STRUCTURE
================================================================================
The following graphics shows STP directory structure after installation
    <STP installation directory> 
    +-- bench.py
    +-- platforms
    |   +-- beaglebone.py
    |   +-- evmskAM335x.py
    +-- README.md
    +-- runstp.py
    +-- src
    |   +-- equipment_info.py
    |   +-- __init__.py
    +-- test_suites
        +-- hello_world
        |   +-- helloworld_s_func_bin.py
        |   +-- helloworld_s_func_load_w_template.py
        +-- templates
            +-- __init__.py
            +-- load_template.py
            +-- test_defaults.py
        
            
4) HOW TO ADD NEW STP TESTS:
================================================================================
You only need to add files to at least two directories:
 - test_suites/<area>/ : Contains the test logic files (.py python scripts). Where area refers to the area/ip/peripheral for which you are writing
   the test. For example, i2c, uart, etc
   
 - The test scripts excersize the binaries compiled with the Starterware release, during test execution the appropiate binary is loaded into the board
   and ran. STP assumes the following root location for the binaries used during the tests.
   <STP installation directory>/../binary/<architecture i.e armv7a>/<compiler i.e. gcc>/<soc i.e. am335x>/<evm i.e evmskAM335x>/....
   The binary used by the test script should be located somewhere downstream of this path preferably following Starterware binaries output structure 
   <STP installation directory>/../binary/<architecture i.e armv7a>/<compiler i.e. gcc>/<soc i.e. am335x>/<evm i.e evmskAM335x>/<project name>/Release/<project binary>.bin
 
 - test_suites/templates/: (Optional) Files (.py python scripts) with logic that can be reused in multiple test scripts
 
5) STP TESTS IMPLEMENTATION GUIDELINES
================================================================================
5.1) TEST CASES
 * Write your test script code using python API.
 * Write your test binaries using C code and the Starterware libraries

5.2) TEST FILES NAME
 *  The test file name should identify the test step.
     Use following convention to name the test files so that the test cases can be 
     selectively run based on AREA, SCOPE and/or TYPE.  
     <AREA>_<SCOPE>_<TYPE>_<OPT_ID>,
      i.e. NAND_S_FUNC_RW.py or NAND_M_PERF_ALL-SIZES.py 
     
     The AREA defines the area the test is targeting, For example i2c, EEPROM, edma, etc.
     
     The SCOPE are used to indicate the amount of time require to run
     the tests, giving users ability to filter test cases based on estimated
     execution time.
     SCOPE TAGS:
      'S', 'M', 'L'  (for Small, Medium and Large tests)
      
    The TYPE Tag specified the type of test it is
    TYPE TAGS:
      FUNC, PERF,STRESS,USECASE,COMPLIANCE (Type of tests being run: Functional, Performance, Stress, Use-case, Compliance) 
           
    The OPT_ID Tag defines additional information regarding this test.
    
5.3) PYTHON FUNCTIONS PROVIDED BY STP
* STP provides the following functions and variables to aide in test case development:
    - serial_load(bin_path, root_path)
        Function to load binary into platform. Can be called with only bin_path as parameter serial_load(bin_path).
        Takes bin_path and root_path as inputs. bin_path is a string containing the path of the binary to be loaded relative to root_path. root_path is a string
        containing the path of the base directory of bin_path, this parameter points to
          <STP installation directory>/../binary/<architecture i.e armv7a>/<compiler i.e. gcc>/<soc i.e. am335x>/<evm i.e evmskAM335x>/
        by default
        Returns True if successful False otherwise
        
    - runstp_import(module_path)
        Function to import templates in test cases with access to runstp objects within the module. This function allows reuse of code across test scripts.
        Takes module_path as input, a string containing the path of the module being imported, relative to <STP install location>. 
        Returns: Nothing
      
    - platform
        This variable provides an abstraction of the device being tested, it is initialized to a pxexpect object that uses a serial connection to communicate with
        the board being tested. With this variable the test script is able to send strings to board via platform.send(..), platform.sendline(...), etc and wait for other
        strings from the board via platform.expect(....) for more information see http://pexpect.sourceforge.net/pexpect.html and http://www.noah.org/wiki/pexpect
    
5.4) FIRST PYTHON STATEMENT IN TEST CASE
 * The first python statement in every test case should be requires = ['a', 'b', 'c' ....]
   The requires = [...] statement is used to specify ARCH, DRIVER, SOC and/or MACHINE 
   requirements to run the test scenario. Each element in the list is considered a "must" i.e
   requires = ['a','b',c'] --> 'a' && 'b' && 'c'; for test cases that can run with "either/or" element 
   make list [...] for that element, i.e. requires = [['a','b','c']] ---> 'a' || 'b' || 'c'. Combinations of
   both are allowed for example   
   
   requires = ['eth', 'spi_master']
   To run this test the platform must have an ethernet driver and a 
   spi_master driver

   requires = ['am3517-evm']
   This test can only be run on an am3517 EVM.

   requires = [['mmc', 'nand'], "uart"]
   This test requires mmc or nand, and UART

 
6) HOW TO ADD NEW PLATFORMS
================================================================================
 * From platform/..., copy the platform file for the board that most resembles the new platform 
    being added to platforms/<your platform>. <your platform> name is typically the evm name.
    For example evmskAM335x.py, evmAM335x.py, beaglebone.py.
    
 * Modify your platform file based on the capabilities supported by the new evm
   The platform file identifies the architecture, the SoC, the evm and the
   supported drivers list. The supported drivers list is list of string indentifying the
   drivers supported in the platform.  Please note the first 3 lines of the platform file MUST identify, the 
   architecture, SoC and EVM respectively, follow by the driver list.
   
   Sample platform file:
    arch = 'armv7a'
    soc = 'am335x'
    platform = 'evmskAM335x'
    interfaces = [
    'uart',
    'i2c',
    'pru',
    'icss',
     .
     .
     .]
     

6.2) HOW TO INSTALL
================================================================================
 *STP is based on python so python needs to be install on your system to be able to run STP. 
 
 *STP is a git project hosted on github, therefore, git needs to be installed on you system to access the code.
 
 * STP relies on the following python packages that are not part of the standard python release:
    - pexpect
        This package implements the expect functionality in python. To install follow the instructions at http://www.noah.org/wiki/pexpect#Download_and_Installation . 
        You might need to install it as sudo 
    - pyserial
        This package implements the serial communication functionality in python. To install follow the instructions at http://pyserial.sourceforge.net/pyserial.html#installation
        You might need to install it as sudo 
    - xmodem
        This module implements the xmodem transfer protocol in python. To install:
            1. Obtain the package from http://pypi.python.org/pypi/xmodem
            2. Decompress the archive
            3. cd to the decompress location and run "sudo python setup.py install:
        
 * cd to <Starterware installation directory> and clone the project with git clone https://github.com/ajhb/stp.git

7) HOW TO RUN TESTS
================================================================================
 * All test cases are run by running ./runstp.py from the <STP install location>. runstp.py takes the following command line options:
         Usage: runstp.py [options]

        Options:
          -h, --help            show this help message and exit
          -f FILE, --folders=FILE
                                Execute runstp testsuites (comma separated)
          -t TESTCASES, --testcases=TESTCASES
                                Execute runstp testcases name patterns (comma
                                separated)
          -p PLATFORM, --platform=PLATFORM
                                Platform being used in the tests (mandatory)
          -b BENCH_PATH, --bench=BENCH_PATH
                                File containing equipment connectivity and setup info
                                (defaults to <stp folder>/bench.py)
          -c COMPILER, --compiler=COMPILER
                                Compiler user to generate test case binaries
                                (gcc,cgt_ccs,etc)

 * -p used to specify the platform being tested.
   The platform name specified with -P option must exist in the platforms/ dir.
   And a entry related to the platform setup must be added to the file pointed
   by option -b.

 * -b used to specify the path of a python file where all the information regarding the setup of the equipment used for testing is found.
    For each equipment there should be a new EquipmentInfo object instantiated that provides the information.  The EquipmentInfo take two parameter as input:
            -- the first paramters is the board name used to identify which setup information should be used for testing, by matching the -p command line parameter
            -- the second parameter is an id used to differentiate two or more boards of the same type. Currently this feature is not implemented but it is there for future use.
    During a test a board is selected by matching the parameter passed as -p in the command line with the board name passed to EquipmentInfo.
    Currently, only board serial connection information is supported in the framework.
    This option defaults to <stp folder>/bench.py
 
 * -f used to specify a comma separated list of areas to test. 
    For example for -f area1,area2 STP will select all possible test cases from test_suites/<area1> and test_suites/<area1> 
 
 * -f In addition to selecting test areas using -s option, users can also 
   specify test cases using -t <python PATTERN>. This option
   selects test cases based on the test case patterns specified in section 5.2.

 * -c specifies the compiler used to build the test binaries. It defaults to gcc
 
 If neither -f or -t are specified test cases are filtered based on the requires statement in each test case. 
 If both -f and -t are specified all test cases belonging to areas -f and test cases that match patterns in -t will be selected to run.  



   
