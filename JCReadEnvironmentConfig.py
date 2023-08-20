"""
This module reads yml config file and assigns the values to passed defaultParameters dictionary

"""
import os
import sys
import re
from collections import defaultdict
import JCGlobalLib


def JCReadEnvironmentConfig( 
    fileName, defaultParameters, yamlModulePresent, debugLevel, logFileName, thisHostName, OSType):
    """
    This function reads environment config file

    # Parameter name needs to be unique across all sections - OS, Environment, Network, Site, Component and Host
    # Parameters can be defined under OS, Environment, Network, Site, Component and Host
    # Parameter value can be redefined in other sections to override previous value.
    # Parameters under OS will be read first, under Environment next, Network, Site, Component and Host in that order.
    # While reading parameters under Environment, if a value is present under specific Environment, 
    #   it will be stored as latest desired value, overriding the value previously defined under OS
    # While reading parameters under Network, if a value is present under specific Network, 
    #   it will be stored as latest desired value, overriding the value previously defined under OS or Environment

    Parameters passed: 
        config file name - yml file name containing parameter spec
        defaultParameters dictionary to update with values read
        yamlModulePresent = True or False
        debugLevel - 0 to 3, 3 being max
        logFileName - log file to log messages
        thisHostName - current host name, used to match the hostname spec
        OSType - current host's OS type

    Returned value
        True if success, False if file could not be read

    """

    returnStatus = True

    if os.path.isfile(fileName) == False:
        print("ERROR JCReadEnvironmentConfig() File |{0}| not found".format(fileName))
        return False

    # use limited yaml reader when yaml is not available
    if yamlModulePresent == True:
        try:
            import yaml
            with open(fileName, "r") as file:
                defaultParametersSpec = yaml.load(file, Loader=yaml.FullLoader)
                file.close()
        except OSError as err:
            errorMsg = "ERROR JCReadEnvironmentConfig() Can not open configFile:|{0}|, OS error: {1}\n".format(
                fileName, err)
            print(errorMsg)
            JCGlobalLib.LogMsg(errorMsg,  logFileName, True, True)
            return False
    else:
        defaultParametersSpec = JCGlobalLib.JAYamlLoad(fileName)

    errorMsg = ''

    # Get global definitions (not environment specific)
    if 'LogFilePath' in defaultParametersSpec:
        defaultParameters['LogFilePath'] = defaultParametersSpec['LogFilePath']

    if 'Platform' in defaultParametersSpec:
        defaultParameters['Platform'] = defaultParametersSpec['Platform']

    # read OS section first
    if 'OS' in defaultParametersSpec:
        for key, value in defaultParametersSpec['OS'].items():
            if key == 'All' or key == 'ALL':
                # if parameters are not yet defined, read the values from this section
                # values in this section work as default if params are defined for
                # specific environment
                JCGlobalLib.JCGatherEnvironmentSpecs(
                        False, # store value if not present already
                        value, debugLevel, defaultParameters, [], [])

            # store definitions matching to current OSType
            if key == OSType:
                # read all parameters defined for this environment
                JCGlobalLib.JCGatherEnvironmentSpecs(
                    True, # store current value if prev value is present
                    value, debugLevel, defaultParameters, [], [])
                defaultParameters['OS']  = key

    # read Component section next
    if 'Component' in defaultParametersSpec:
        for key, value in defaultParametersSpec['Component'].items():
            if key == 'All' or key == 'ALL':
                # if parameters are not yet defined, read the values from this section
                # values in this section work as default if params are defined for
                # specific environment
                JCGlobalLib.JCGatherEnvironmentSpecs(
                        False, # store value if not present already
                        value, debugLevel, defaultParameters, [], [])

            # match current hostname to hostname specified within each environment to find out
            #   which environment spec is to be applied for the current host
            if value.get('HostName') != None:
                if re.match(value['HostName'], thisHostName):
                    # current hostname match the hostname specified for this environment
                    # read all parameters defined for this environment
                    JCGlobalLib.JCGatherEnvironmentSpecs(
                        True, # store current value if prev value is present
                        value, debugLevel, defaultParameters, [], [])
                    defaultParameters['Component'] = key

    # read Environment section last
    if 'Environment' in defaultParametersSpec:
        for key, value in defaultParametersSpec['Environment'].items():
            if key == 'All' or key == 'ALL':
                # if parameters are not yet defined, read the values from this section
                # values in this section work as default if params are defined for
                # specific environment
                JCGlobalLib.JCGatherEnvironmentSpecs(
                        False, # store value if not present already
                        value, debugLevel, defaultParameters, [], [])

            # match current hostname to hostname specified within each environment to find out
            #   which environment spec is to be applied for the current host
            if value.get('HostName') != None:
                if re.match(value['HostName'], thisHostName):
                    # current hostname match the hostname specified for this environment
                    # read all parameters defined for this environment
                    JCGlobalLib.JCGatherEnvironmentSpecs(
                        True, # store current value if prev value is present, parameters under Environment takes precedence
                        value, debugLevel, defaultParameters, [], [])
                    defaultParameters['Environment']  = key


    if OSType == "Windows":
        if 'CommandShell' not in defaultParameters:
            ### chekc if powershell 7 is present
            if os.path.exists('C:/Program Files/PowerShell/7/pwsh.exe'):
                defaultParameters['CommandShell'] = 'C:/Program Files/PowerShell/7/pwsh.exe -NonInteractive -command'
            else:
                defaultParameters['CommandShell'] ="TBD"

    ### exand any environment variables used in path definitions
    if 'JCHome' in defaultParameters:
        defaultParameters['JCHome'] = os.path.expandvars(defaultParameters['JCHome'])
    if 'JCLogFilePath' in defaultParameters:
        defaultParameters['JCLogFilePath'] = os.path.expandvars(defaultParameters['JCLogFilePath'])
    if 'JCConfigPath' in defaultParameters:
        defaultParameters['JCConfigPath'] = os.path.expandvars(defaultParameters['JCConfigPath'])
    if 'JCTemplatePath' in defaultParameters:
        defaultParameters['JCTemplatePath'] = os.path.expandvars(defaultParameters['JCTemplatePath'])

    ### create log file path if does not exist
    if 'JCLogFilePath' in defaultParameters:
        logFilePath = defaultParameters['LogFilePath']
    else:
        if 'JCHome' in defaultParameters:
            logFilePath = defaultParameters['JCHome'] + "/Logs"

    ### if logFilePath does not end with '/', add it
    if re.match(r'/$', logFilePath) == None:
        logFilePath = '{0}/'.format(logFilePath)
    defaultParameters['JCLogFilePath'] = logFilePath

    if os.path.exists(logFilePath) == False:
        try:
            os.mkdir(logFilePath)
        except OSError as err:
            errorMsg = "ERROR JCReadEnvironmentConfig() Could not create logs directory:{0}".format(
                logFilePath, err )
            print( errorMsg)
            sys.exit(0)

    if 'SitePrefixLength' not in defaultParameters:
        defaultParameters['SitePrefixLength'] = 3

    if debugLevel > 1:
        print('DEBUG-2 JCReadEnvironmentConfig() Content of config file: {0}, read to  ConfigEnvironment: {1}'.format(
            fileName, defaultParameters))
    elif debugLevel > 0:
        print('DEBUG-1 JCReadEnvironmentConfig() Read environment config file:|{0}|'.format(fileName))

    if errorMsg != '':
        print(errorMsg)
        JCGlobalLib.LogMsg(errorMsg,  logFileName, True, True)

    return True
    
