""" 
This script parses the configuration spec file to derive parameter values based on OS, environment, network, site,
component and host level, then, prepares the configuration file(s) by replacing the variables with variable values in 
template configuration file(s).

Parameters passed: Review the JCHelp() for details.
    
Note - did not add python interpreter location at the top intentionally so that
    one can execute this using python or python3 depending on python version on target host

Author: havembha@gmail.com, 2023-08-19

Execution flow
   Get OSType, OSName, OSVersion
   Based on python version, check for availability of yml module
   Read JCEnvironment.yml and allow commands config file
   Delete log files older than 7 days (not supported on windows yet)
   Read configuration spec file
   Replace variable names with variable values in template config file(s)
"""

import os
import sys, signal
import re
import time
import platform
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader
from jinja2 import exceptions
from jinja2 import StrictUndefined

import JCGlobalLib
import JCReadEnvironmentConfig

### define global variables
JCVersion = "JC01.00.01"

# default config file has environment specific definitions
environmentFileName = "JCEnvironment.yml"

debugLevel = 0
logFileName  = 'JCConfigGen.log'

# default parameters read from app config file name
defaultParameters = {}

def JCConfigExit(reason):
    """
    convenient functoin print & log error and exit.
    """
    print(reason)
    JCGlobalLib.LogMsg(reason,  logFileName, True, True)
    sys.exit()

def JCHelp():
    helpString1 = """
    python3 JCConfigGen.py -t <templateFileName1>[,<templateFileName2>,..] [-c <configFileName1>[,<configFileName2>,...]] 
        -s <siteNamePrefixLength> [-e <environmentSpec>] [-h <hostName or host's IP>] [-T <templatePath>] [-C <configPath>]
    
    -t <templateFileName1>[,<templateFileName2>,..] - template file names in CSV form.
        this template file format uses jinja2 spec (https://jinja.palletsprojects.com/en/3.1.x/)
        the template files are rendered using jinja render function
        Mandatory parameter

    [-c <configFileName1>[,<configFileName2>,...]] - config file name(s) in the same order as the template file name(s)
        Optional parameter, defaults to config file name of <configPath>/<templateFileName1>, 
         <configPath>/<templateFileName2>,...

    [-s <siteNamePrefixLength>] - integer value indicating the length of siteName in hostName starting from start of the hostName.
        This value is used to derive the JCSiteName from hostName and then use JCSiteName variable to derive other hostnames at the site
        while rendering the environment specification file.
        Optional parameter, defaults to 5

    [-e <environmentSpec>] - file contaning the variable definitions at OS, component, and environment level. 
        Optional parameter, defaults to JCEnvironment.yml file in current path

    [-h <hostName>] - short hostname based on how the variable substituion need to occur
        Optional parameter, if not passed, derived from current hostname where the this rool runs. 
        Using the hostname, OS, component and environment are derived as specified in environment spec file.
          After that, applicable specs based on OS, component and environment are read from environment spec file.

    [-T <templatePath>] - absolute or relative path where template files are present
        Optional parameter, defaults to JCTemplatePath defined in environment spec
            If the path starts with ./, it is considered as relative path to current working path
            If the path starts with /, it is considered as absolute path

    [-C <configPath>] - absolute or relative path where config files are to be written
        Optional parameter, defaults to JCConfigPath defined in environment spec
            If the path starts with ./, it is considered as relative path to current working path
            If the path starts with /, it is considered as absolute path
        Note - <templatePath> and <configPath> can't be same

    """

    helpString2 = """
    [-D <debugLevel>] - 0 no debug, 1, 2, 3, 3 being max level
        default is 0, no debug
        
    [-l <logFileName>] - log file name
        Defaults to the terminal in the interactive mode
        Defaults to JCConfigGen.log.YYYYmmddHHMMSS in non-interactive mode
    """

    helpString3 = """
    Examples:
        python3 JCConfigGen.py -s 5 -t WSConfig.xml
            First 5 letters of current hostname; where JCConfigGen.py was invoked, are used to form JCSiteName variable. 
            Since environment spec is not passed, default file name of JCEnvironment.yml is used.
            Since template path is not passed, JCTemplatePath defined in environment spec is used.
            Since config path is not passed, JCConfigPath defined in environment spec is used
            Since no config file name is passed, it generates the config file with name <configPath>/WSConfig.xml
            If called in non-interactive mode, uses default file name - JCConfigGen.log.YYYYmmddHHMMSS
            If ran in interactive mode, logs are printed to terminal
            No debug info printed (default debug of 0)

        python3 JCConfigGen.py -t WSConfig.xml -e WSEnvironmentVariables.yml
            Since site name prefix is not passed, expect the JCSiteName is being set in environment spec file using
               the python function JCString()
            Since template path is not passed, JCTemplatePath defined in environment spec is used.
            Since config path is not passed, JCConfigPath defined in environment spec is used
            Since no config file is passed, it generates the config file with name <configPath>/WSConfig.xml
            If called in non-interactive mode, uses default log file name - JCConfigGen.log.YYYYmmddHHMMSS
            If ran in interactive mode, logs are printed to terminal
            No debug info printed (default debug of 0)

        python3 JCConfigGen.py -s 5 -t WSConfig.xml -c WSConfig.xml -e WSEnvironmentVariables.yml 
            Since template path is not passed, JCTemplatePath defined in environment spec is used.
            Since config path is not passed, JCConfigPath defined in environment spec is used
            Writes the config to the given file name - <configPath>/WSConfig.xml

        python3 JCConfigGen.py  -t WSConfig.xml,ASConfig.xml -c WSConfig.xml,ASConfig.xml -e EnvironmentVariables.yml
            Creates <configPath>/WSConfig.xml after rendering the template file <templatePath>/WSConfig.xml
            Creates <configPath>/ASConfig.xml after rendering the template file <templatePath>/ASConfig.xml
            Here common environment variable file is passed that applies to both template files.

        python3 JCConfigGen.py -s 5 -t WSConfig.xml -c WSConfig.xml -e EnvironmentVariables.yml -T ./Templates -C ./Conf
            Uses the relative template path of ./Templates
            Uses the relative config path of ./Conf
            Writes the config to the given file name - ./Conf/WSConfig.xml

        python3 JCConfigGen.py -s 5 -t WSConfig.xml -c WSConfig.xml -D 3 -e EnvironmentVariables.yml
            Writes the config to the given file name - <configPath>/WSConfig.xml
            Prints debug level 3 messages
           
        python3 JCConfigGen.py -s 5 -t WSConfig.xml -c WSConfig.xml -D 3 -l WSConfig.log -e EnvironmentVariables.yml
            Writes the output to the given file name - <configPath>/WSConfig.xml
            Prints debug level 3 messages to the log file with name WSConfig.log

        python3 JCConfigGen.py -s 5 -t WSConfig.xml -c WSConfig.xml -e EnvironmentVariables.yml -h hostName1
            siteNamePrefix length and hostName are passed to generate the config file while generating the config file on host other than target host.
            (off line config generation)

        python JCConfigGen.py -V version <-- print version
        python JCConfigGen.py -H help    <-- print this message

        python functions available inside environment spec file
            JCString( string, startPostion, endPosition) - use this to extract desird number of characters from a string
              by passing starting position (0 based) and end position.
                ### extract 3 letters from hostname as siteName, do not print new line
                {% set JCSiteName = JCString("dfwhost", 0, 3) -%}
            JCHostNameToIPAddress( hostname )
                get host's IP address
                {% set myIP = JCHostNameToIPAddress( JCHostName ) -%}
            JCHostNamesToIPAddresses( [hostnames] )
                get IP addresses of host names in an list
                {% set my_site_host_names = [ appServer1, appServer2, WebServer1] %}
                {% set my_site_ips = JCHostNamesToIPAddresses( my_site_host_names ) %}
            JCHostNameToIPSegment( hostname )
                get segment address of given host (first three octet of IP address)
                {% set myIPSegment = JCHostNameToIPSegment( JCHostName ) -%} 
            JCSetVariable( name, value )
                set the variable value in the memory to be carried forward while processing other
                   templates read via include
    """
    print(helpString1)
    print(helpString2)
    print(helpString3)
    return None

### install signal handler to exit upon ctrl-C
def JCSignalHandler(sig, frame):
    JCConfigExit("Control-C pressed")

signal.signal(signal.SIGINT, JCSignalHandler)

### display help if no arg passed
if len(sys.argv) < 2:
    JCHelp()
    sys.exit()

### parse arguments passed
# this dictionary will have argument pairs
# to find the value of an arg, use argsPassed[argName]
argsPassed = {}

JCGlobalLib.JCParseArgs(argsPassed)

### formulate the command so that the command used to generate the output file can be added to the 
###   config file header for traceability / debugging any issues
JCCommand = 'python3 JCConfigGen.py '

templateFileNames = None       
if '-t' in argsPassed:
    templateFileNames = argsPassed['-t']
    JCCommand += " -t {0}".format(templateFileNames)
    templateFileNamesList = list(map(str.strip, templateFileNames.split(',')))
else:
    print("ERROR JCConfigGen() mandatory parameter template file name is not passed")
    JCHelp()
    sys.exit()

outputFileNames = None

commandLineTemplatePath = commandLineConfigPath = None

if '-T' in argsPassed:
    ### use template path passed
    tempPath = argsPassed['-T']
    if tempPath == "./":
        tempPath = os.getcwd()
    commandLineTemplatePath = tempPath
    JCCommand += " -T {0}".format(tempPath)
else:
    ### template path not passed
    ### if ./Templates exists, use that path.
    ### else, use current working path itself
    if os.path.exists("{0}/templates".format(os.getcwd())) == True:
        commandLineTemplatePath = "{0}/templates".format( os.getcwd() ) 
    else:
        commandLineTemplatePath = os.getcwd()

if '-C' in argsPassed:
    tempPath = argsPassed['-C']
    if tempPath == "./":
        tempPath = os.getcwd()
    commandLineConfigPath = tempPath
    JCCommand += " -C {0}".format(tempPath)
    if commandLineTemplatePath != None:
        if commandLineTemplatePath == commandLineConfigPath:
            errorMsg = "ERROR JCConfigGen() TemplatePath:{0} and ConfigPath:{1} can't be same to avoid file being overwritten\n".format(
                commandLineTemplatePath, commandLineConfigPath )
            JCConfigExit(errorMsg)
else:
    commandLineConfigPath = "{0}/conf".format(os.getcwd())

if os.path.exists(commandLineConfigPath) == False:
    os.mkdir(commandLineConfigPath)
    if os.path.exists(commandLineConfigPath) == False:
        JCConfigExit('ERROR, config path:{0} is not present, can not create it either, exiting'.format(
            commandLineConfigPath) )

if commandLineTemplatePath == commandLineConfigPath:
    errorMsg = "ERROR JCConfigGen() TemplatePath:{0} and ConfigPath:{1} can't be same to avoid file being overwritten\n".format(
        commandLineTemplatePath, commandLineConfigPath )
    JCConfigExit(errorMsg)

if '-e' in argsPassed:
    # environment file name passed.
    environmentFileName = argsPassed['-e']
    if debugLevel > 0:
        print("DEBUG-1 JCConfigGen() configFileName passed: {0}".format(environmentFileName))

JCCommand += " -e {0}".format(environmentFileName)
    
if '-s' in argsPassed:
    siteNamePrefix = int(argsPassed['-s'])
    JCCommand += " -s {0}".format(siteNamePrefix)
else:
    siteNamePrefix = 5

if '-h' in argsPassed:
    thisHostName = argsPassed['-h']
    JCCommand += " -h {0}".format(thisHostName)
else:
    thisHostName = platform.node()

# if hostname has domain name, strip it
hostNameParts = thisHostName.split('.')
defaultParameters['JCHostName'] = thisHostName = hostNameParts[0]
if siteNamePrefix != None:
    defaultParameters['JCSiteName'] = thisHostName[ :siteNamePrefix]
else:
    defaultParameters['JCSiteName'] = ''
defaultParameters['JCSiteName3Chars'] = thisHostName[ :3]
defaultParameters['JCSiteName4Chars'] = thisHostName[ :4]
defaultParameters['JCSiteName5Chars'] = thisHostName[ :5]
defaultParameters['JCSiteName6Chars'] = thisHostName[ :6]

if '-c' in argsPassed:
    outputFileNames = argsPassed['-c']
    JCCommand += " -c {0}".format(outputFileNames)
    outputFileNamesList = list(map(str.strip, outputFileNames.split(',')))
else:
    outputFileNamesList = []
    ### use template names as the source to make output file names
    ###   append hostname to make each output file unique
    for tempTemplateFileName in templateFileNamesList:
        tempOutputFileName = "{0}.{1}".format( tempTemplateFileName, thisHostName )
        outputFileNamesList.append( tempOutputFileName )

if '-l' in argsPassed:
    JCCommand += " -l {0}".format(argsPassed['-l'])
    try:
        # log file requested, open in append mode
        outputFileHandle = open ( argsPassed['-l'], "a")
    except OSError as err:
        errorMsg = "ERROR JCConfigGen() Can not open output file:|{0}|, OS error: {1}\n".format(argsPassed['-l'], err)
        JCConfigExit(errorMsg)
else:
    outputFileHandle = None

if '-D' in argsPassed:
    debugLevel = int(argsPassed['-D'])
    JCCommand += " -D {0}".format(debugLevel)
if debugLevel > 0 :
    print("DEBUG-1 JCConfigGen() Version {0}\nParameters passed: {1}".format(JCVersion, argsPassed))

if '-V' in argsPassed:
    print(JCVersion)
    sys.exit()
    
if '-H' in argsPassed:
    JCHelp()
    sys.exit()

# get OSType, OSName, and OSVersion. These are used to execute different python
# functions based on compatibility to the environment
OSType, OSName, OSVersion = JCGlobalLib.JCGetOSInfo(sys.version_info, debugLevel)

### check whether yaml module is present
yamlModulePresent = JCGlobalLib.JCIsYamlModulePresent()

### save the command used to generate the output file so that it can be added to the config file header if opted
defaultParameters['JCCommand'] = JCCommand
defaultParameters['JCDateTime'] = JCGlobalLib.JCGetDateTime(0)
defaultParameters['JCOSType'] = OSType
defaultParameters['JCOSName'] = OSName
defaultParameters['JCOSVersion'] = OSVersion

### store the command line passed values for template and config paths so that these override the values 
###  that may be present in environment spec file.
if commandLineTemplatePath != None:
    defaultParameters['JCTemplatePath'] = os.path.expandvars(commandLineTemplatePath)
if os.path.exists( defaultParameters['JCTemplatePath']) == False:
    JCConfigExit('ERROR, template path:{0} is not present, exiting'.format(defaultParameters['JCTemplatePath'] ))

if commandLineConfigPath != None:
    defaultParameters['JCConfigPath'] = os.path.expandvars(commandLineConfigPath)

### define colors to print messages in different color
myColors = {
    'red':      ['',"\033[31m",'<font color="red">'], 
    'green':    ['',"\033[32m",'<font color="green">'], 
    'yellow':   ['',"\033[33m",'<font color="yellow">'], 
    'blue':     ['',"\033[34m",'<font color="blue">'], 
    'magenta':  ['',"\033[35m",'<font color="magenta">'], 
    'cyan':     ['',"\033[36m",'<font color="cyan">'], 
    'clear':    ['',"\033[0m",'</font>'], 
    }

# reportFormat is passed, set the color index
HTMLBRTag = ''
if '-r' in argsPassed:
    if re.match('HTML|html', argsPassed['-r']) :
        # this index needs to match the index at HTML tags for diff colors are assigned in myColors dictionary
        colorIndex = 2
        HTMLBRTag = "<br>"
    elif re.match('color', argsPassed['-r']) :
        # this index needs to match the index at which VT100 terminal color codes are assigned in myColors dictionary
        colorIndex = 1
    else:
        # no color coding of lines
        colorIndex = 0
else:
    # defaults to color
    colorIndex = 1

if debugLevel > 2:
    # test LogLine() with test lines
    myLines = """ERROR - expect to see in red color
ERROR, - expect to see in red color
WARN   - expect to see in yellow color
PASS   - expect to see in green color
"""
    JCGlobalLib.LogLine(myLines, True, myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

returnResult = "_JAConfigGen_PASS_" # change this to other errors when error is encountered

environmentTERM = os.getenv('TERM')
### determin current session type using the term environment value, sleep for random duration if non-interactive 
if environmentTERM == '' or environmentTERM == 'dumb':
    interactiveMode = False

    ### for non-interactive mode, if log file not opened yet, open it in append mode
    if outputFileHandle == None:
        tempOutputFileName = '{0}/{1}.{2}'.format(
            defaultParameters['JCLogFilePath'],
            logFileName,
            JCGlobalLib.UTCDateForFileName())
        try:
            outputFileHandle = open ( tempOutputFileName, "a")
        except OSError as err:
            JCGlobalLib.LogLine(
                    "ERROR JCConfigGen() Can't open output file:{0}, OSError: {1}".format( tempOutputFileName, err ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

else:
    interactiveMode = True

import socket
def JCHostNameToIPAddress( hostName):
    """
    This function returns the IP address of hostName
    """
    tempIPAddress = None
    try:
        tempIPAddress = socket.gethostbyname(hostName)
    except socket.gaierror:
        JCGlobalLib.LogLine(
                "ERROR JCHostNameToIPAddress() socket.gethostbyname() resulted in gaierror, error getting IP address of hostName:{0} ".format( hostName ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
    except Exception as error:
        JCGlobalLib.LogLine(
                "ERROR JCHostNameToIPAddress() socket.gethostbyname() resulted in error: {0}, error getting IP address of hostName:{1} ".format(error, hostName ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

    return tempIPAddress

def JCHostNameToIPSegment( hostname ):
    """
    Return the first three octects of IP address (skip last octet)
    Use this to find the IP segment address of hostname
    """
    tempIPAddress = JCHostNameToIPAddress( hostname)
    if ( tempIPAddress != None ):
        lastDotPosition = tempIPAddress.rfind( '.')
        return ( tempIPAddress[0:lastDotPosition])
    else:
        return("ERROR xlating hostname to IP")
    
def JCHostNamesToIPAddresses( hostNames):
    """
    This function returns the IP addresses array of hostNames passed in array
    """
    ipAddressArray = []
    for hostName in hostNames:
        tempIPAddress = JCHostNameToIPAddress( hostName)
        if tempIPAddress != None:
            ipAddressArray.append( tempIPAddress )
        else:
            ipAddressArray.append( "ERROR xlating hostname to IP" )
    return ipAddressArray

def JCString(myString, startPos, endPos):
    """
    This function returns the substring within the given start and end positions
    """
    if myString == None:
        return ""
    if startPos == None:
        ## return from start of string
        startPos = 0
    if endPos == None:
        ## return till end of string
        return myString[startPos:]
    
    return myString[startPos:endPos]

def JCSetVariable( name, value ):
    """
    This function stores the value of key in defaultParameters dictionary
    """
    global defaultParameters, templateEnvironment
    templateEnvironment.globals[name] = value
    # defaultParameters[name] = value
    return True

### below functions can be called within the template
JCFunctions = {
    "JCHostNameToIPAddress": JCHostNameToIPAddress,
    "JCString": JCString,
    "JCSetVariable": JCSetVariable,
    "JCHostNameToIPSegment": JCHostNameToIPSegment,
    "JCHostNamesToIPAddresses": JCHostNamesToIPAddresses,
}
### 
PATH = os.path.dirname(os.path.abspath(__file__))
templateEnvironment = Environment(
    autoescape=False,
    loader=FileSystemLoader(defaultParameters['JCTemplatePath']),
    undefined=StrictUndefined,
    trim_blocks=False)

### render environment spec file to include other files within the main file
def JCRenderTemplateFile(templateEnvironment, templateFileName, configFileName, function_dict ):
    global defaultParameters, interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType
    returnStatus = False
    sortedDefaultParameters = ''
    for key, value in sorted(defaultParameters.items()):
        sortedDefaultParameters += "{0}: {1}\n".format(key, value)
    try:
        with open(configFileName, 'w') as outputFile:
            try:
                tempTemplate = templateEnvironment.get_template(templateFileName)
                tempTemplate.globals.update(function_dict)
                outputText = tempTemplate.render(defaultParameters)
                outputFile.write(outputText)
                outputFile.close()
                if debugLevel > 0:
                    JCGlobalLib.LogLine(
                        "DEBUG-1 JCRenderTemplateFile() Generated output file:|{0}| from template file:|{1}|".format(
                                configFileName, templateFileName ),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
                returnStatus = True

            except exceptions.FilterArgumentError:
                JCGlobalLib.LogLine(
                    "ERROR JCRenderTemplateFile() - FilterArgumentError - Error processing the template file:{0} using jinja2 get_template()".format(
                            templateFileName ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

            except exceptions.SecurityError as error:
                JCGlobalLib.LogLine(
                    "ERROR JCRenderTemplateFile() - SecurityError - Error processing the template file:{0} using jinja2 get_template(), error:{1}".format(
                            templateFileName, error ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

            except exceptions.TemplateAssertionError:
                JCGlobalLib.LogLine(
                    "ERROR JCRenderTemplateFile() - TemplateAssertionError - Error opening the template file:{0} using jinja2 get_template()".format(
                            templateFileName ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

            except exceptions.TemplateError as error:
                tempLineNumber =  tempMessage = ''

                if hasattr(error, 'lineno') and error.lineno is not None:
                    tempLineNumber = error.lineno
                if hasattr(error, 'message') and error.message is not None:
                    tempMessage = error.message
                
                JCGlobalLib.LogLine(
                    " JCRenderTemplateFile() - TemplateError - Error rendering template file:{0} using variable values:{1}\nERROR {2}, lineno: {3}, message:{4}".format(
                            templateFileName, sortedDefaultParameters, error, tempLineNumber, tempMessage ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

            except exceptions.TemplateSyntaxError as error:
                JCGlobalLib.LogLine(
                    " JCRenderTemplateFile() - TemplateSyntaxError - Error rendering template file:{0} using variable values:{1}\nERROR {2}".format(
                            templateFileName, sortedDefaultParameters, error ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

            except exceptions.TemplateRuntimeError:
                JCGlobalLib.LogLine(
                    "ERROR JCRenderTemplateFile() - TemplateRuntimeError - Error opening the template file:{0} using jinja2 get_template()".format(
                            templateFileName ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            except exceptions.UndefinedError as error:
                JCGlobalLib.LogLine(
                    " JCRenderTemplateFile() - UndefinedError - Error rendering the template file:{0} using variable values:{1}\nERROR {2}".format(
                            templateFileName,  sortedDefaultParameters, error),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            except OSError as error:
                JCGlobalLib.LogLine(
                    "ERROR JCRenderTemplateFile() unknown error while processing the template file:{0}, error:{1}".format(
                            templateFileName, error ),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            
    except OSError as error:
        JCGlobalLib.LogLine(
            "ERROR JCRenderTemplateFile() Could not open config file:{0}, error:{1}".format(configFileName, error ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
    return returnStatus

def JCMergeIncludeFile( fileName, outputFile):
    """
    This function reads all lines from fileName,
    checks each line one by one for the presence of {% include <fileName> %}
        If present, calls itself to process that include file
        If not present, writes current line to output file
    """
    global defaultParameters
    returnStatus = False
    if os.path.isfile( fileName) == False:
        ### check under the default template path
        fileName = "{0}/{1}".format(defaultParameters['JCTemplatePath'], fileName)
        if os.path.isfile( fileName ) == False:
            JCGlobalLib.LogLine(
                "ERROR JCMergeIncludeFile() File not found, template fileName:{0}".format(fileName ),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            return returnStatus
    file = open( fileName, "r")
    lines = file.readlines()
    file.close()

    ### {% include <fileName> %}
    regexString = re.compile(r'\{%(\s+)(include)(\s+)"(.+)"(\s+)%\}')
    ### ignore commented include line in the form
    ### # {% include <fileName> %}
    ###    ## {% include <fileName %}
    ignoreLine = re.compile(r'^#|(\s+)(#+)(\s+)(\{%)')

    for line in lines:
        try:
            ### search for "{% include * %}" pattern in current line
            returnVariables = regexString.findall( line )
            if ( len( returnVariables) > 0 ):
                ### if current line starts with '#', ignore this line
                if ignoreLine.match(line):
                    outputFile.write(line)
                    continue
                
                ### found include statement, process this include file
                ###   include file name at 4th position
                JCMergeIncludeFile( returnVariables[0][3], outputFile)
            else:
                ### save current line in merged file
                outputFile.write(line)

        except OSError as error:
            JCGlobalLib.LogLine(
                "ERROR JCMergeIncludeFile() Error writing line to file, error:{0}".format(error ),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            return False
    
    return returnStatus

def JCMergeAllIncludeFiles( sourceFileName, saveFileName ):
    returnStatus = True
    if os.path.isfile( sourceFileName) == False:
        return returnStatus
    
    try:
        with open(saveFileName, 'w') as outputFile:
            ### process the given file
            JCMergeIncludeFile( sourceFileName, outputFile)

    except OSError as error:
        JCGlobalLib.LogLine(
            "ERROR JCMergeAllIncludeFiles() Could not open the file:{0}, error:{1}".format(sourceFileName, error ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

    return returnStatus


if ( os.path.exists("./temp") == False ):
    os.mkdir("./temp")
    if ( os.path.exists("./temp") == False ):
        JCConfigExit("ERROR ./temp does not exist, not able to create it")

if sys.version_info.major < 3:
    JCConfigExit("ERROR minimum python version needed is 3.6, current host has python:{0}".format(sys.version_info))


if sys.version_info.minor < 2:
    mergedEnvironmentFileName = os.path.join(defaultParameters['JCTemplatePath'] , environmentFileName)
    ### if python version is less than 3.10, jinja2 3.0 does not carry the context forward.
    ###   read all include files to a single file and process it together so that context is properly available for jinja2
    ### this file needs to be in template folder for jinja2 rendering to occur
    mergedFileName = "{0}/{1}.include.{2}".format(
            defaultParameters['JCTemplatePath'], 
            environmentFileName,
            thisHostName )
    if( JCMergeAllIncludeFiles(mergedEnvironmentFileName, mergedFileName) == True ):
        ### If merge is successful, process the included file
        ### If merge not successful, process the original file as is.

        ### create temp cofig file using original environmentFileName, not with include spec
        tempConfigFile = "./temp/{0}.{1}".format( 
                    environmentFileName,
                    thisHostName )
        ### this file is in template folder
        environmentFileName = "{0}.include.{1}".format(
            environmentFileName,
            thisHostName )
 
else:
    ### process environment spec file as template file so that any include, import type of tasks
    ###   are performed before reading variable values from that file
    tempConfigFile = "./temp/{0}.{1}".format( 
                environmentFileName,
                thisHostName )

returnStatus = JCRenderTemplateFile(
    templateEnvironment,  
    environmentFileName, 
    tempConfigFile, 
    JCFunctions )
if ( returnStatus == False ):
    JCConfigExit('ERROR JCConfigGen() error rendering the environment spec file:{0}, exiting'.format(environmentFileName))
else:
    JCGlobalLib.LogLine(
        "INFO JCConfigGen() Created temporary variable file: {0}, after processing environment file: {1}".format(
                environmentFileName,
                os.path.join(defaultParameters['JCTemplatePath'] , environmentFileName) ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

### read environment definitions from rendered file (expanded with includes / imports etc)
if JCReadEnvironmentConfig.JCReadEnvironmentConfig( 
        tempConfigFile, 
        defaultParameters, 
        yamlModulePresent, 
        debugLevel,  logFileName, thisHostName, OSType ) == False:
    JCConfigExit('Fatal ERROR, exiting')


errorMsg  = "INFO JCConfigGen() Version:{0}, OSType: {1}, OSName: {2}, OSVersion: {3}".format(
    JCVersion, OSType, OSName, OSVersion)
JCGlobalLib.LogLine(
	errorMsg, 
    interactiveMode,
    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

### get current time in seconds
currentTime = time.time()

### if PATH and LD_LIBRARY are defined, set those environment variables
if 'PATH' in defaultParameters:
    os.environ['PATH'] = defaultParameters['PATH']

if 'LD_LIBRARY_PATH' in defaultParameters:
    os.environ['LD_LIBRARY_PATH'] = defaultParameters['LD_LIBRARY_PATH']

if 'JCFileRetencyDurationInDays' in defaultParameters:
    JCFileRetencyDurationInDays = defaultParameters['JCFileRetencyDurationInDays']
else:
    JCFileRetencyDurationInDays = defaultParameters['JCFileRetencyDurationInDays'] = 7

if OSType == 'Windows':
    ### get list of files older than retency period
    filesToDelete = JCGlobalLib.JCFindModifiedFiles(
            '{0}/{1}*'.format(defaultParameters['JCLogFilePath'], logFileName), 
            currentTime - (JCFileRetencyDurationInDays*3600*24), ### get files modified before this time
            debugLevel, thisHostName)
    if len(filesToDelete) > 0:
        for fileName in filesToDelete:
            try:
                os.remove(fileName)
                if debugLevel > 3:
                    JCGlobalLib.LogLine(
                        "DEBUG-4 JCConfigGen() Deleting the file:{0}".format(fileName),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            except OSError as err:
                JCGlobalLib.LogLine(
			        "ERROR JCConfigGen() Error deleting old log file:{0}, errorMsg:{1}".format(fileName, err), 
                	interactiveMode,
                	myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
                
else:
    # delete log files covering logs of operations also.
    command = 'find {0} -name "{1}*" -mtime +{2} |xargs rm'.format(
        defaultParameters['JCLogFilePath'], logFileName, JCFileRetencyDurationInDays)
    if debugLevel > 1:
        JCGlobalLib.LogLine(
            "DEBUG-2 JCConfigGen() purging files with command:{0}".format(command),
            interactiveMode,
            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

    returnResult, returnOutput, errorMsg = JCGlobalLib.JCExecuteCommand(
            defaultParameters['JCCommandShell'],
            command, debugLevel, OSType)
    if returnResult == False:
        if re.match(r'File not found', errorMsg) != True:
            if debugLevel > 1:
                JCGlobalLib.LogLine(
                    "DEBUG-2 JCConfigGen() No older log files to delete, {0}".format(errorMsg), 
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)



for index in range( len(templateFileNamesList)):
    configFileName = os.path.join( defaultParameters['JCConfigPath'], outputFileNamesList[index])
    templateFileNameWithPath = os.path.join( defaultParameters['JCTemplatePath'], templateFileNamesList[index])
    templateFileName = templateFileNamesList[index]
    if os.path.isfile(templateFileNameWithPath) == False:
        JCGlobalLib.LogLine(
                "ERROR JCConfigGen() template file {0} not found".format(templateFileName),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
        continue
    returnStatus =  JCRenderTemplateFile(templateEnvironment, templateFileName, configFileName, JCFunctions )
    if ( returnStatus == False ):
        JCConfigExit('ERROR JCConfigGen() error rendering the environment spec file: {0}, exiting'.format(templateFileName))
    else:
        JCGlobalLib.LogLine(
            "INFO JCConfigGen() Created config file: {0}, after processing template file: {1}".format(
                configFileName,
                templateFileName),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
