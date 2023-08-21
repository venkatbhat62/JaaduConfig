""""
    This module contains global functions used by JCdoo Config

    GetGMTTime() - returns string with current GMT time the form YYYY/MM/DD hh:mm:ss.sss
    JCYamlLoad(fileName) - reads the yaml file, returns data in dictionary

    Author: havembha@gmail.com, 2023-08-19
"""
import datetime
import platform
import re
import sys
import os
import time

def UTCDateTime():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

def UTCDateTimeForFileName():
    return datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

def UTCDate():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def UTCDateForFileName():
    return datetime.datetime.utcnow().strftime("%Y%m%d")

def UTCTime():
    return datetime.datetime.utcnow().strftime("%H:%M:%S")

def JCConvertStringTimeToTimeInMicrosec( dateTimeString, format:str):
    """
    JCGlobalLib.JAConvertStringTimeToTimeInMicrosec( dateTimeString, format:str)

    Converts date time string to time in microsec using the format string. 
    If successful, returns time in microseconds
    Else, returns 0

    """
    # 2022-06-04 add logic to use timezone while converting time to UTC time ???
    try:
        datetime_obj = datetime.datetime.strptime(dateTimeString, format)
        if sys.version_info[0] < 3 or sys.version_info[1] < 4:
            timeInMicroSeconds =  time.mktime(datetime_obj.timetuple()) * 1000000
        else:
            timeInMicroSeconds = datetime_obj.timestamp() * 1000000
        return timeInMicroSeconds
    except:
        return 0

def JCParseArgs(argsPassed):
    """
    JCGlobalLib.JAParseArgs(argsPassed)

    Parses the command level arguments in sys.argv[] to the list argsPassed
    Returns argument count

    """
    args = sys.argv[1:]
    argc = len(args)
    for index in range(0,argc,2):
        argument = args[index]
        argsPassed[argument] = args[index+1]
            
    return argc

def JCIsYamlModulePresent():
    """
    JCGlobalLib.JAIsYamlModulePresent()

    This function checks whether yaml module is present.
    If present, returns True
    Else, returns False

    """
    yamlModulePresent = False
    try:
        if sys.version_info.major >= 3 and sys.version_info.minor >= 3:
            import importlib
            from importlib import util
            try: 
                if util.find_spec("yaml") != None:
                    yamlModulePresent = True
                else:
                    yamlModulePresent = False
            except ImportError:
                yamlModulePresent = False

        else:
            yamlModulePresent = False
    except:
        yamlModulePresent = False
    return yamlModulePresent

def JCGetTime( deltaSeconds:int ):
    """
    JCGlobalLib.JAGetTime( deltaSeconds:int )

    This function takes current time, subtracts the given time in seconds and 
       returns the resulting time in HH:MM:SS format.

    """
    tempTime = datetime.datetime.now()
    deltaTime = datetime.timedelta(seconds=deltaSeconds)
    newTime = tempTime - deltaTime
    return newTime.strftime("%H:%M:%S")

def JCGetDateTime( deltaSeconds:int ):
    """
    JCGlobalLib.JAGetDateTime( deltaSeconds:int )
    This function takes current time, subtracts the given time in seconds and 
       returns the resulting time in YYYY-MM-DDTHH:MM:SS.mmmmmmZ format.

    """
    tempTime = datetime.datetime.now()
    deltaTime = datetime.timedelta(seconds=deltaSeconds)
    newTime = tempTime - deltaTime
    return newTime.strftime("%Y-%m-%dT%H:%M:%S.%f%Z")

def JCGetDayOfMonth( deltaSeconds:int ):
    """
    JCGlobalLib.JAGetDayOfMonth( deltaSeconds:int )
    This function takes current time, subtracts the given time in seconds and 
        returns day of the month

    """
    tempTime = datetime.datetime.now()
    deltaTime = datetime.timedelta(seconds=deltaSeconds)
    newTime = tempTime - deltaTime
    newTimeString = newTime.strftime("%d")
    return newTimeString 

def LogMsg(logMsg:str, fileName:str, appendDate=True, prefixTimeStamp=True):
    """"
    JCGlobalLib.LogMsg(logMsg:str, fileName:str, appendDate=True, prefixTimeStamp=True)

    Logs the given message to a log file in append mode, 
      if appendDate is True, file name ending with YYYYMMDD is assumed.
      If prefixTimeStamp is True, current dateTime string is prefixed to the log line before logging

    """
    if fileName == None:
        print(logMsg)
        return 0
        
    if appendDate == True:
        logFileName = "{0}.{1}".format( fileName, UTCDateForFileName())
    else:
        logFileName = fileName

    try:
        logFileStream = open( logFileName, 'a')
    except OSError:
        return 0
    else:
        if ( prefixTimeStamp == True) :
            logFileStream.write( UTCDateTime() + " " + logMsg )
        else:
            logFileStream.write(logMsg )
        logFileStream.close()
        return 1

def LogLine(myLines, tempPrintLine, myColors, colorIndex:int, outputFile:str, HTMLBRTag:str,  diffLine=False, OSType='Linux'):
    """
    JCGlobalLib.LogLine(myLines, tempPrintLine, myColors, colorIndex:int, outputFile:str, HTMLBRTag:str,  diffLine=False, OSType='Linux')

    This function logs the lines passed in myLines to terminal with colors based on first word seen in first line
    If tempPrintLine passed is True, formatted line will be printed to the terminal
    While printing first line, current timestamp is printed as first two words

    Formatting applied to all lines when first word is
    ^ERROR |^ERROR, - red
    ^DIFF - blue
    ^PASS |^ PASS - gren
    ^INFO - no color
    ^FAIL |^WARN - yellow

    If subsequent lines start with 
    < - printed in blue color
    > - printed in cyan color
    These lines are considerd as output of diff command

    Parameters passed:
        myLines - line to print
        tempPrintLine - True or False, if True, formatted line will be printed to the terminal

    """

    currentTime = UTCDateTime() + ' '
    tempLines = myLines.splitlines(False)

    for line in tempLines:
        if colorIndex == 2:
            line = line.replace("<!--",  "/&lt;!--")
            line = line.replace("-->",  "--&gt;")
        
        # repace \r with \n
        line = line.replace(r'\r', r'\n')

        if ( ( (OSType != "Windows") and re.match( '^< ', line) )
            or ( (OSType == "Windows" and re.search(r'<=$' , line) )) 
            and (diffLine == True) ):
            # diff line, color code it
            line = myColors['blue'][colorIndex]  + line + myColors['clear'][colorIndex]
        elif ( ( (OSType != "Windows") and re.match( '^> ', line) )
            or ( (OSType == "Windows" and re.search(r'=>$' , line) )) 
            and (diffLine == True) ):
            # diff line, color code it
            line = myColors['magenta'][colorIndex] + line + myColors['clear'][colorIndex]
        elif re.match( '^ERROR |^ERROR,', line):
            # diff line, color code it
            line = myColors['red'][colorIndex] + currentTime + line + myColors['clear'][colorIndex]
        elif re.match( '^PASS |^ PASS', line):
            # diff line, color code it
            line = myColors['green'][colorIndex] + currentTime + line + myColors['clear'][colorIndex]    
        elif re.match('^DIFF ', line) :
            line = myColors['cyan'][colorIndex] + currentTime + line + myColors['clear'][colorIndex]   
        elif re.match('^INFO ', line) :
            line = currentTime + line   
        elif re.match('^WARN |^FAIL ', line) :
            line = myColors['yellow'][colorIndex] + currentTime + line + myColors['clear'][colorIndex]   
        if outputFile != None:
            outputFile.write( HTMLBRTag + line + '\n')
        if tempPrintLine == True:
            print( line )

def JCYamlLoad(fileName:str ):
    """
    JCGlobalLib.JAYamlLoad(fileName:str )

    Basic function to read config file in yaml format
    Use this on host without python 3 or where yaml is not available

    Upon successful read, returns the yaml data in dictionary form

    """

    from collections import defaultdict
    import re
    yamlData = defaultdict(dict)
    paramNameAtDepth = {0: '', 1: '', 2: '', 3:'', 4: ''}
    leadingSpacesAtDepth = {0: 0, 1: None, 2: None, 3: None, 4: None}
    prevLeadingSpaces = 0
    currentDepth = 0
    currentDepthKeyValuePairs = defaultdict(dict)

    try:
        with open(fileName, "r") as file:
            depth = 1

            while True:
                tempLine =  file.readline()
                if not tempLine:
                    break
                # SKIP comment line
                if re.match(r'\s*#', tempLine):
                    continue

                tempLine = tempLine.rstrip("\n")
                if re.match("---", tempLine) :
                    continue
                if len(tempLine) == 0:
                    continue
                # remove leading and trailing spaces, newline
                lstripLine = tempLine.lstrip()
                if len(lstripLine) == 0:
                    continue

                ## separate param name and value, split to two parts, the value itself may have ':'
                params = lstripLine.split(':', 1)
                ## remove leading space from value field
                params[1] = params[1].lstrip()

                # based on leading spaces, determine depth
                leadingSpaces = len(tempLine)-len(lstripLine)
                if leadingSpaces == prevLeadingSpaces:

                    if leadingSpaces == 0:
                        if params[1] == None or len(params[1]) == 0 :
                            # if value does not exist, this is the start of parent/child definition
                            paramNameAtDepth[currentDepth+1] = params[0]

                        else:
                            # top layer, assign the key, value pair as is to yamlData
                            yamlData[params[0]] = params[1]
                    else:
                        # store key, value pair with current depth dictionary
                        currentDepthKeyValuePairs[params[0]] = params[1]

                    leadingSpacesAtDepth[currentDepth+1] = leadingSpaces

                elif leadingSpaces < prevLeadingSpaces:
                    # store key, value pair of prev depth 
                    for key, values in currentDepthKeyValuePairs.items():
                        if currentDepth == 1:
                            if paramNameAtDepth[1] not in yamlData.keys() :
                                yamlData[ paramNameAtDepth[1]] = {}
                            
                            yamlData[ paramNameAtDepth[1] ][key] = values

                        elif currentDepth == 2:
                            if paramNameAtDepth[1] not in yamlData.keys() :
                                yamlData[ paramNameAtDepth[1]] = {}
                            if paramNameAtDepth[2] not in yamlData[paramNameAtDepth[1]].keys() :
                                yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]] = {}

                            yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]][key] = values
                        elif currentDepth == 3:
                            if paramNameAtDepth[1] not in yamlData.keys() :
                                yamlData[ paramNameAtDepth[1]] = {}
                            if paramNameAtDepth[2] not in yamlData[paramNameAtDepth[1]].keys() :
                                yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]] = {}
                            if paramNameAtDepth[3] not in yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]].keys() :
                                yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]][paramNameAtDepth[3]] = {}
                            yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]][paramNameAtDepth[3]][key] = values

                    currentDepthKeyValuePairs = defaultdict(dict)
                    
                    if leadingSpacesAtDepth[currentDepth-1] == leadingSpaces:
                        currentDepth -= 1
                    elif leadingSpacesAtDepth[currentDepth-2] == leadingSpaces:
                        currentDepth -= 2
                    elif leadingSpacesAtDepth[currentDepth-3] == leadingSpaces:
                        currentDepth -= 3
                    prevLeadingSpaces = leadingSpaces

                    if params[1] == None or len(params[1]) == 0 :
                        # if value does not exist, this is the start of parent/child definition
                        paramNameAtDepth[currentDepth+1] = params[0]
                elif leadingSpaces > prevLeadingSpaces:
                    leadingSpacesAtDepth[currentDepth+1] = leadingSpaces
                    currentDepth += 1
                    prevLeadingSpaces = leadingSpaces
                    if params[1] == None or len(params[1]) == 0 :
                        # if value does not exist, this is the start of parent/child definition
                        paramNameAtDepth[currentDepth+1] = params[0]
                    else:
                        # save current key, value 
                        currentDepthKeyValuePairs[params[0]] = params[1]

            for key, values in currentDepthKeyValuePairs.items():
                if currentDepth == 1:
                    if paramNameAtDepth[1] not in yamlData.keys() :
                        yamlData[ paramNameAtDepth[1]] = {}
                            
                    yamlData[ paramNameAtDepth[1] ][key] = values

                elif currentDepth == 2:
                    if paramNameAtDepth[1] not in yamlData.keys() :
                        yamlData[ paramNameAtDepth[1]] = {}
                    if paramNameAtDepth[2] not in yamlData[paramNameAtDepth[1]].keys() :
                        yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]] = {}

                    yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]][key] = values
                elif currentDepth == 3:
                    if paramNameAtDepth[1] not in yamlData.keys() :
                        yamlData[ paramNameAtDepth[1]] = {}
                    if paramNameAtDepth[2] not in yamlData[paramNameAtDepth[1]].keys() :
                        yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]] = {}
                    if paramNameAtDepth[3] not in yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]].keys() :
                        yamlData[ paramNameAtDepth[1]][paramNameAtDepth[2]][paramNameAtDepth[3]] = {}
                    yamlData[paramNameAtDepth[1]][paramNameAtDepth[2]][paramNameAtDepth[3]][key] = values
            file.close()
            return yamlData

    except OSError as err:
        print('ERROR Can not read file:|' + fileName + '|, ' + "OS error: {0}".format(err) + '\n')
        return yamlData

def JCFindModifiedFiles(fileName:str, sinceTimeInSec:int, debugLevel:int, thisHostName:str):
    """
    JCGlobalLib.JAFindModifiedFiles(fileName:str, sinceTimeInSec:int, debugLevel:int, thisHostName:str)

        This function returns file names in a directory that are modified since given GMT time in seconds
        if sinceTimeInSec is 0, latest file is picked up regardless of modified time
        Can be used instead of find command 

        if sinceTimeInSec is +ve number, files modified before that time are returned
        if sinceTimeInSec is -ve number, files modified since that time are returned

    """
    head_tail = os.path.split( fileName )
    # if no path specified, use ./ (current working directory)
    if head_tail[0] == '' or head_tail[0] == None:
        myDirPath = './'
    else:
        myDirPath = head_tail[0]

    fileNameWithoutPath = head_tail[1]

    # if fileName has variable {HOSTNAME}, replace that with current short hostname
    if re.search(r'{HOSTNAME}', fileNameWithoutPath) != None:
        fileNameWithoutPath = re.sub(r'{HOSTNAME}', thisHostName, fileNameWithoutPath)

    if debugLevel > 1 :
        print('DEBUG-2 JCFileFilesModified() filePath:{0}, fileName: {1}'.format( myDirPath, fileNameWithoutPath))

    import fnmatch
    import glob

    if sinceTimeInSec > 0:
        findFilesOlderThanGivenTime = True
    else:
        # make the number +ve for comparison later
        sinceTimeInSec = abs(sinceTimeInSec)
        findFilesOlderThanGivenTime = False

    fileNames = {}

    try:
        # get all file names in desired directory with matching file spec
        for file in glob.glob(myDirPath + "/" + fileNameWithoutPath):
        
            if debugLevel > 2 :
                print('DEBUG-3 JCFileFilesModified() fileName: {0}, match to desired fileNamePattern: {1}'.format(
                    file, fileNameWithoutPath) )

            # now check the file modified time, if greater than or equal to passed time, save the file name
            fileModifiedTime = os.path.getmtime ( file )
            if findFilesOlderThanGivenTime == True:
                if fileModifiedTime < sinceTimeInSec :
                    fileNames[ fileModifiedTime ] = file 
                    if debugLevel > 2 :
                        print('DEBUG-3 JCFileFilesModified() fileName: {0}, modified time: {1}, later than desired time: {2}'.format( file, fileModifiedTime, sinceTimeInSec) )

            else:
                if fileModifiedTime >= sinceTimeInSec :
                    fileNames[ fileModifiedTime ] = file 
                    if debugLevel > 2 :
                        print('DEBUG-3 JCFileFilesModified() fileName: {0}, modified time: {1}, later than desired time: {2}'.format( file, fileModifiedTime, sinceTimeInSec) )
    except OSError as err:
        errorMsg = "ERROR JCFileFilesModified() Not able to find files in fileName: {0}, error:{1}".format( 
            myDirPath, err)
        print( errorMsg)
        
    sortedFileNames = []
    for fileModifiedTime, fileName in sorted ( fileNames.items() ):
        sortedFileNames.append( fileName )

    if debugLevel > 0 :
        print('DEBUG-1 JCFileFilesModified() modified files in:{0}, since gmtTimeInSec:{1}, fileNames:{2}'.format( 
            fileName, sinceTimeInSec, sortedFileNames) )

    # if sinceTimeInSec is zero, pick up latest file only
    if sinceTimeInSec == 0:
        if len(sortedFileNames) > 0:
            # return single file as list
            return [sortedFileNames[-1]]
    
    return sortedFileNames

def JCGetOSInfo(pythonVersion, debugLevel:int):
    """
    JCGlobalLib.JAGetOSInfo(pythonVersion, debugLevel:int)

    Returns 
        OSType like Linux, Windows
        OSName like rhel for Redhat Linux, ubuntu for Ubuntu, Windows for Windows
        OSVersion like
            7 (for RH7.x), 8 (for RH8.x) for Redhat release
            20 (for Ubuntu)
            10, 11 for Windows

    """
    OSType = platform.system()
    if OSType == 'Linux' :
        try:
            with open("/etc/os-release", "r") as file:
                while True:
                    tempLine = file.readline()
                    if not tempLine:
                        break
                    if len(tempLine)<5:
                        continue
                    tempLine = re.sub('\n$','',tempLine)

                    if re.match(r'ID=', tempLine) != None:
                        dummy, OSName = re.split(r'ID=', tempLine)

                        # remove double quote around the value
                        OSName = re.sub('"','',OSName)

                    elif re.match(r'VERSION_ID',tempLine) != None:
                        dummy,tempOSVersion = re.split(r'VERSION_ID=', tempLine)
                file.close()
        except:
            try:
                with open("/etc/system-release", "r") as file:
                    while True:
                        tempLine = file.readline()
                        if not tempLine:
                            break
                        if len(tempLine)<5:
                            continue
                        tempLine = re.sub('\n$','',tempLine)
                        # line is of the form: red hat enterprise linux server release 6.8 (santiago)
                        #                                                             \d.\d <-- OSVersion
                        myResults = re.search( r'Red Hat (.*) (\d.\d) (.*)', tempLine)
                        if myResults != None:
                            tempOSVersion = myResults.group(2)
                            OSName = 'rhel'

            except:
                try:
                    with open("/etc/redhat-release", "r") as file:
                        while True:
                            tempLine = file.readline()
                            if not tempLine:
                                break
                            if len(tempLine)<5:
                                continue
                            tempLine = re.sub('\n$','',tempLine)
                            # line is of the form: red hat enterprise linux server release 6.8 (santiago)
                            #                                                             \d.\d <-- OSVersion
                            myResults = re.search( r'Red Hat (.*) (\d.\d) (.*)', tempLine)
                            if myResults != None:
                                tempOSVersion = myResults.group(2)
                                OSName = 'rhel'
                except:
                    tempOSVersion = ''
                    OSName = ''
                    print("ERROR JCGetOSInfo() Can't read file: /etc/os-release or /etc/system-release")
                    tempOSReease = ''

    elif OSType == 'Windows' :
        if pythonVersion >= (3,7) :
            tempOSVersion = platform.version()
        OSName = OSType

    # extract major release id from string like x.y.z
    # windows 10.0.19042
    # RH7.x - 3.10.z, RH8.x - 4.18.z
    # Ubuntu - 5.10.z
    OSVersion = re.search(r'\d+', tempOSVersion).group()
    if debugLevel > 0 :
        print("DEBUG-1 JCGetOSInfo() OSType:{0}, OSName:{1}, OSVersion:{2}".format(OSType, OSName, OSVersion) )

    return OSType, OSName, OSVersion
     

def JCGetOSType():
    """
    JCGlobalLib.JAGetOSType()
        Returns values like Linux, Windows
    """
    return platform.system()

def JCExecuteCommand(shell:str, command:str, debugLevel:int, OSType="Linux", timeoutPassed=30, nowait=False):
    """
    JCGlobalLib.JAExecuteCommand(shell:str, command:str, debugLevel:int, OSType="Linux", timeoutPassed=30)

    Execute given command
      If OSType is windows, replace \r with \n, remove [...], 
         normalize the output to standard multiline string similar to output from Unix host

    Return status
        returnResult - True on success, False on failure
        returnOutput - command execution result
        errorMsg - message indicating the success or failure condition

    """
    import subprocess
    
    returnResult = False
    returnOutput = ''

    if debugLevel > 2:
        print("DEBUG-3 JCExecuteCommand() shell:{0}, command:|{1}|".format(shell, command))

    if nowait == True:
        errorMsg = ''
        DETACHED_PROCESS = 0x00000008
        ### just run the command, DO NOT wait for it to complete
        if OSType == 'Windows':
            result = subprocess.Popen( shell + " " + command, 
                shell=False, stdin=None, stdout=None, stderr=None,
                close_fds=True, creationflags=DETACHED_PROCESS )

        else:
            ### separate words of given shell command to list
            shell = re.split(' ', shell)
            shell.append( command )
            result = subprocess.Popen( args=shell,  
                shell=False, stdin=None, stdout=None, stderr=None,
                close_fds=True)

        if result.returncode == 0:
            returnResult = False
        else:
            returnResult = True
    else:
        try:
            if OSType == 'Windows':
                result = subprocess.run( shell + " " + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,timeout=timeoutPassed)

            else:
                ### separate words of given shell command to list
                shell = re.split(' ', shell)
                shell.append( command )
                result = subprocess.run( args=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE,timeout=timeoutPassed)

            if result.returncode == 0:
                if OSType == 'Windows':
                    ### replace \r\n with \n
                    returnOutput = result.stdout.decode('utf-8')
                    returnOutput = re.sub(r'\r\n', '\n', returnOutput)
                    returnOutput = re.sub(r'\r', '\n', returnOutput)
                    ### if only \r is present, replace it with \n
                    returnOutput = returnOutput.rstrip("\n")
                    returnOutput = returnOutput.split('\n')
                else:
                    returnOutput = result.stdout.decode('utf-8').rstrip("\n")
                    returnOutput = returnOutput.split('\n')
                errorMsg = 'INFO JCExecuteCommand() result of executing the command:|{0} {1}|, result:\n{2}'.format(shell, command,returnOutput)
                returnResult = True
            else:
                ### execution failed
                if OSType == 'Windows':
                    errorMsg = result.stderr.decode('utf-8')
                    errorMsg = re.sub(r'\r', '\n', errorMsg)
                    ### if only \r is present, replace it with \n
                    errorMsg = errorMsg.rstrip("\n")
                    errorMsg = errorMsg.split('\n')
                else:
                    errorMsg = result.stderr.decode('utf-8').split('\n')

                if OSType == 'Windows':
                    returnOutput = result.stdout.decode('utf-8')
                    returnOutput = re.sub(r'\r', '\n', returnOutput)
                    ### if only \r is present, replace it with \n
                    returnOutput = returnOutput.rstrip("\n")
                    returnOutput = returnOutput.split('\n')
                else:
                    returnOutput = result.stdout.decode('utf-8').split('\n')

                lenErrorMsg = len(errorMsg)
                if lenErrorMsg == 1:
                    lenErrorMsg = len(errorMsg[0])
                if lenErrorMsg > 0:
                    errorMsg = 'ERROR JCExecuteCommand() failed to execute command:|{0} {1}|, errorMsg:|{2}|'.format(shell, command, errorMsg)
                    returnResult = False
                else:
                    ### this is a case where command itself was executed, returned result from that command is not 0 (not success)
                    ### since there was no error response, use stdout to process the result further.
                    ### when two files are different, diff command returns status code 1 with stderr empty, diff lines in stdout
                    errorMsg = ''
                    returnResult = True

        except (subprocess.CalledProcessError) as err :
            errorMsg = "ERROR JCExecuteCommand() failed to execute command:|{0} {1}|, called process error:|{2}|".format(shell, command, err)

        except subprocess.TimeoutExpired as err:
            errorMsg = "WARN JCExecuteCommand() timeout while executing the command:|{0} {1}|, called process error:|{2}|".format(shell, command, err)
            returnOutput = ''

        except ( FileNotFoundError ) as err:
            errorMsg = "INFO JCExecuteCommand() File not found, while executing the command:|{0} {1}|, error:|{2}|".format(shell, command, err)
            
        except Exception as err:
            errorMsg = "ERROR JCExecuteCommand() failed to execute command:|{0} {1}|, exception:|{2}|".format(shell, command, err)


    if debugLevel > 2 :
        print("DEBUG-3 JCExecuteCommand() command output:|{0}|, message:|{1}|".format(returnOutput, errorMsg))
    # returnOutput = str(returnOutput)
    return returnResult, returnOutput, errorMsg

def JCGetProfile(fileName:str, paramName:str):
    """
    JCGlobalLib.JAGetProfile(fileName:str, paramName:str)

    Searches for the paramName in given profile file having the values in the format
        paramName: paramValue 
    
    Parameters passed:
        fileName - profile file name
        paramName - parameter name to search

    Returns
       returnStatus - True if value found, else False
       paramValue - value if value found, else None

    """
    returnStatus = False
    paramValue = None
    if os.path.exists(fileName) :
        with open(fileName, "r") as file:
            while True:
                line = file.readline()
                if not line:
                    break
                line = line.strip()
                fieldParts = line.split(':')
                if len(fieldParts) > 1:
                    if fieldParts[0] == paramName:
                        paramValue = fieldParts[1]
                        paramValue = paramValue.lstrip()
                        returnStatus = True
                        break
            file.close()
    else:
        print("ERROR JCGetProfile() Profile file:{0} is not present".format(fileName))

    return returnStatus, paramValue

def JCSetProfile(fileName:str, paramName:str, paramValue:str):
    """
    JCGlobalLib.JASetProfile(fileName:str, paramName:str, paramValue:str)

    Searches for the paramName in given profile file having the values in the format
        paramName: paramValue 
    Replaces the maching line with new paramValue passed

    Parameters passed:
        fileName - profile file name
        paramName - parameter name to search
        paramValue - parameter value

    Returns
       returnStatus - True if value found, else False
       
    """
    returnStatus = True
    fileContents = ''
    lineFound = False
    replaceLine = "{0}: {1}\n".format(paramName,paramValue)
    if os.path.exists(fileName) :
        with open(fileName, "r") as file:
            while True:
                line = file.readline()
                if not line:
                    break
                fieldParts = line.split(':')
                if len(fieldParts) > 1:
                    if fieldParts[0] == paramName:
                        ### make new line with new param value
                        fileContents += replaceLine
                        lineFound = True
                    else:
                        ### store original line as is
                        fileContents += (line )
            if lineFound == False:
                ### add new line
                fileContents += (replaceLine)
            file.close()
        
        with open(fileName, "w") as file:
            file.write(fileContents)
            file.close()

    else:
        ### write new file
        with open(fileName, "w") as file:
            file.write(replaceLine)
            file.close()

    return returnStatus

def JCDeriveConfigFileName( pathName1:str, pathName2:str, configFileName:str, subsystem:str, operation:str, version:str, debugLevel:int ):
    """
    JCGlobalLib.JADeriveConfigFileName( pathName1:str, pathName2:str, configFileName:str, subsystem:str, operation:str, version:str, debugLevel:int )

    Prepare operation specific configuration file
    <path>/<configFileName>.<subsystem>.<operation>.[.<version>].<fileType>
    
    if subsystem passed is empty, 'Apps' subsystem is used by default
    if version is not empty, it is added to the filename

    if operation is 'stats', and if file name does not exist with subsystem name, operation, 
      and file does exist with configFileName, that base name is returned.

    """

    returnStatus = False
    errorMsg = ''
    
    if debugLevel > 1:
        print("DEBUG-2 JCDeriveConfigFileName() pathName1:|{0}|, pathName2:|{1}|, configFileName:|{2}|, subsystem:|{3}|, operation:|{4}|, version:|{5}|".format(
                pathName1, pathName2, configFileName, subsystem, operation, version))

    # remove file type from configFileName
    baseConfigFileNameWithoutFileType, fileType = configFileName.split('.')

    ### use Apps subsystem as default 
    if subsystem == '' or subsystem == None:
        subsystem = 'Apps'
    
    ### first try with version, if version is passed
    if version != '':
        ### first try under path1
        tempConfigFileName = '{0}/{1}.{2}.{3}.{4}.{5}'.format(
            pathName1, baseConfigFileNameWithoutFileType, subsystem, operation, version, fileType)
        if os.path.exists( tempConfigFileName ) == False:
            ### Now try under pathName2
            tempConfigFileName = '{0}/{1}.{2}.{3}.{4}.{5}'.format(
                pathName2, baseConfigFileNameWithoutFileType, subsystem, operation, version, fileType)
            if os.path.exists( tempConfigFileName ) == False:
                returnStatus = False
            else:
                returnStatus = True
        else:
            returnStatus = True

    if returnStatus == False:
        ### try without the version string
        tempConfigFileName = '{0}/{1}.{2}.{3}.{4}'.format(
            pathName1, baseConfigFileNameWithoutFileType, subsystem, operation, fileType)
        if os.path.exists( tempConfigFileName ) == False:
            tempConfigFileName = '{0}/{1}.{2}.{3}.{4}'.format(
                pathName2, baseConfigFileNameWithoutFileType, subsystem, operation, fileType)
            if os.path.exists( tempConfigFileName ) == False:
                ### if operation is 'stats' or 'logs', look for base file name itself
                if operation == 'stats' or operation == 'logs':
                    tempConfigFileName = '{0}/{1}'.format( 
                            pathName1, configFileName)
                    if os.path.exists( tempConfigFileName ) == False:
                        tempConfigFileName = '{0}/{1}'.format( 
                                pathName2, configFileName)
                        if os.path.exists( tempConfigFileName ) == False:
                            ### file does exist, return error
                            errorMsg = "ERROR JCDeriveConfigFileName() config file:|{0}| not present in path1:|{1}|, path2:|{2}|, AppConfig:|{3}|, subsystem:|{4}|, operation:|{5}|, version:|{6}|".format(
                                tempConfigFileName, pathName1, pathName2,  configFileName, subsystem, operation, version)
                            returnStatus = False
                            tempConfigFileName = ''
                        else:
                            returnStatus = True
                    else:
                        returnStatus = True
                else:        
                    ### file does exist, return error
                    errorMsg = "ERROR JCDeriveConfigFileName() config file:|{0}| not present in path1:|{1}|, path2:|{2}|, AppConfig:|{3}|, subsystem:|{4}|, operation:|{5}|, version:|{6}|".format(
                        tempConfigFileName, pathName1, pathName2,  configFileName, subsystem, operation, version)
                    returnStatus = False
                    tempConfigFileName = ''
            else:
                returnStatus = True
        else:
            returnStatus = True

    if debugLevel > 1:
        print("DEBUG-2 JCDeriveConfigFileName() derived config file:|{0}|".format(tempConfigFileName))
    return returnStatus, tempConfigFileName, errorMsg
    
def JCGatherEnvironmentSpecs(storeCurrentValue, values, debugLevel, defaultParameters, integerParameters, floatParameters):
    """
    JCGlobalLib.JAGatherEnvironmentSpecs(storeCurrentValue, values, debugLevel, defaultParameters, integerParameters, floatParameters)

    Read environment spec for a given environment
    This function can be called recursively

    Parameters passed:
        storeCurrentValue - True or False. If True, even if previous value was present for that parameter name,
                new value will be stored in defaultParameters{}
        values - parameter key,value pairs
        debugLevel - 0 to 3, 3 being max level
        defaultParameters - dictionary where values are to be stored
        integerParameters - if current parameter name is in this list, value read will be converted to integer and stored
        floatParameters - if current parameter name is in this list, value read will be converted to float and stored

    Returned value:
        True

    """

    for myKey, myValue in values.items():
        if debugLevel > 2:
            print('DEBUG-3 JCGatherEnvironmentSpecs() key: {0}, value: {1}'.format(myKey, myValue))

        if myKey not in defaultParameters or storeCurrentValue == True:
            try:
                if myKey in integerParameters or myValue.isnumeric():
                    defaultParameters[myKey] = int(myValue)
                elif myKey in floatParameters:
                    defaultParameters[myKey] = float(myValue)
                else:
                    try:
                        ### if value is float, this will not generate exception
                        defaultParameters[myKey] = float(myValue)    
                    except ValueError:
                        # string value, store as is.
                        defaultParameters[myKey] = myValue
            except AttributeError:
                # string value, store as is.
                defaultParameters[myKey] = myValue
    return True

def JCEvaluateCondition(serviceName, serviceAttributes, defaultParameters, debugLevel:int,
    interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType):

    """
    JCGlobalLib.JAEvaluateCondition(serviceName, serviceAttributes, defaultParameters, debugLevel:int,
    interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType)
    
    Executes the serviceAttributes['Command'], and compares the result to the value specified in 
      serviceAttributes['Condition'] 

    The condition spec can be > | < | = and a value 
        The value can be integer or string

    """
    numberOfErrors = 0

    tempCommand = serviceAttributes['Command']
    ### if command spec is present, run the command
    if tempCommand == None:
        conditionPresent = False
        conditionMet = False
    else: 
        conditionPresent = True
        conditionMet = False

        ### now execute the command to get result 
        ###   command was checked for allowed command while reading the config spec
        if OSType == "Windows":
            #tempCommandToEvaluateCondition = '{0} {1}'.format( defaultParameters['JCCommandShell'], tempCommand) 
            tempCommandToEvaluateCondition = tempCommand 
        else:
            tempCommandToEvaluateCondition =  tempCommand
        tempCommandToEvaluateCondition = os.path.expandvars( tempCommandToEvaluateCondition ) 

        if debugLevel > 2:
            LogLine(
                "DEBUG-3 JCEvaluateCondition() name:|{0}|, executing command:|{1}|".format(
                    serviceName, tempCommandToEvaluateCondition),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

        returnResult, returnOutput, errorMsg = JCExecuteCommand(
                                            defaultParameters['JCCommandShell'],
                                            tempCommandToEvaluateCondition, debugLevel, OSType)
        if returnResult == False:
            numberOfErrors += 1
            if re.match(r'File not found', errorMsg) != True:
                LogLine(
                    "ERROR JCEvaluateCondition() name:{0}, File not found, error evaluating the condition by executing command:|{1}|, error:|{2}|".format(
                            serviceName, tempCommandToEvaluateCondition, errorMsg), 
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            else:
                LogLine(
                    "ERROR JCEvaluateCondition() name:{0}, error evaluating the condition by executing command:|{1}|, error:|{2}|".format(
                            serviceName, tempCommandToEvaluateCondition, errorMsg), 
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            conditionMet = False
        else:
            if len(returnOutput) > 0:
                ### take the value from 1st line
                tempConditionResult = returnOutput[0]

                ### based on float, int or string, convert them and assign to conditionResult
                ###  this is to ensure comparison is done with proper data type later
                if re.match(r'(\d+)(\.)(\d+)', tempConditionResult):
                    conditionResult = float(tempConditionResult)
                elif re.match(r'(\d+)', tempConditionResult):
                     conditionResult = int(tempConditionResult) 
                else:
                    conditionResult = str(tempConditionResult)  

                ### assign all lines
                conditionResults = returnOutput

                ### separate the condition field spec ( >|<|=) (value)
                conditionSpecParts = serviceAttributes['Condition'].split(' ')
                if len(conditionSpecParts) > 0:

                    ### if condition result is multiline string, compute the number of lines and compare that to the condition number
                    lengthOfConditionResults = len(conditionResults)
                    if  lengthOfConditionResults > 1:
                        if re.search('>=', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) >= int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<=', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) <= int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('>', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) > int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) < int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('=', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) == int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('!=', conditionSpecParts[0]):
                            if int(lengthOfConditionResults) != int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True

                    elif isinstance(conditionResult, int) :
                        ### numeric string, single line 
                        if re.search('>=', conditionSpecParts[0]):
                            if conditionResult >= int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<=', conditionSpecParts[0]):
                            if conditionResult < int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('>', conditionSpecParts[0]):
                            if conditionResult > int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<', conditionSpecParts[0]):
                            if conditionResult < int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('=', conditionSpecParts[0]):
                            if conditionResult == int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('!=', conditionSpecParts[0]):
                            if conditionResult != int( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                    elif isinstance(conditionResult, float) :
                        ### numeric string float value, single line
                        if re.search('>=', conditionSpecParts[0]):
                            if conditionResult >= float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<=', conditionSpecParts[0]):
                            if conditionResult <= float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('>', conditionSpecParts[0]):
                            if conditionResult > float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<', conditionSpecParts[0]):
                            if conditionResult < float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('=', conditionSpecParts[0]):
                            if conditionResult == float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('!=', conditionSpecParts[0]):
                            if conditionResult != float( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                    else:
                        ### string comparison
                        if re.search('>=', conditionSpecParts[0]):
                            if conditionResult >= str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<=', conditionSpecParts[0]):
                            if conditionResult <= str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('>', conditionSpecParts[0]):
                            if conditionResult > str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('<', conditionSpecParts[0]):
                            if conditionResult < str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('=', conditionSpecParts[0]):
                            if conditionResult == str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True
                        elif re.search('!=', conditionSpecParts[0]):
                            if conditionResult != str( conditionSpecParts[1]):
                                ### condition met
                                conditionMet = True

                        if conditionResult == conditionSpecParts[1] :
                            conditionMet = True              
                    
                    if debugLevel > 1:
                        if conditionMet == False:
                            LogLine(
                                "DEBUG-2 JCEvaluateCondition() item name:|{0}|, condition NOT met, command response:|{1}|, condition:|{2}|, skipping this item".format(
                                    serviceName, conditionResults, serviceAttributes['Condition']),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
                        else:
                            LogLine(
                                "DEBUG-2 JCEvaluateCondition() item name:|{0}|, condition met, command response:|{1}|, condition:|{2}|".format(
                                    serviceName, conditionResults, serviceAttributes['Condition']),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
                else:
                    LogLine(
                        "WARN JCEvaluateCondition() name:|{0}|, invalid condition:|{1}|, expecting spec in the form: (> | < | =) (value), example: > 5".format(
                            serviceName, serviceAttributes['Condition']),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            else:
                ### empty response, nothing to compare to. Declare condition not met
                conditionResult = ''
                conditionResults = []
                conditionMet = False
                if debugLevel > 0:
                    LogLine(
                        "DEBUG-1 JCEvaluateCondition() item name:|{0}|, condition NOT met, command response:|{1}|, condition:|{2}|, skipping this item".format(
                            serviceName, conditionResults, serviceAttributes['Condition']),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

    return conditionPresent, conditionMet

def JCDatamaskMaskLine(line, datamaskSpec, debugLevel, interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType):
    """
    JCGlobalLib.JADatamaskMaskLine(line, datamaskSpec, debugLevel, interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType)
    
    if curent line has any of the search string defined in datamask spec,
    replace those strings withe replace strings defined in datamask spec
    
    return line

    """

    if debugLevel > 2:
            LogLine(
                'DEBUG-3 JCDatamaskMaskLine() initial input line:|{0}\n'.format(line),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

    for search, replace in datamaskSpec.items():

        if debugLevel > 3:
            LogLine(
                'DEBUG-4 JCDatamaskMaskLine() input:|{0}|, search:|{1}|, replace:|{2}|\n'.format(
                    line, search, replace),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
        line = re.sub(r'{}'.format(search), r'{}'.format(replace),line )

        if debugLevel > 3:
            LogLine(
                'DEBUG-4 JCDatamaskMaskLine() output line :|{0}\n'.format(line),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
    if debugLevel > 2:
        LogLine(
            'DEBUG-3 - JCDatamaskMaskLine() final output line:|{0}\n'.format(line),
            interactiveMode,
            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

    return line

def JCDataMaskFile(fileName, datamaskSpec, debugLevel, interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType):
    """
    JCDatamaskMaskFile(fileName, logFilePath, datamaskSpec, debugLevel, interactiveMode, myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType)

    This function applies datamask, translates given file to a temporary file with xlated strings.

    """
    returnStatus = True
    newFileName = "{0}.datamasked".format(fileName)
    try:
        with open(newFileName, "w") as newFile:
            try:
                with open( fileName, "r") as origFile:
                    while True:
                        ### reach each line from origFile, xlate the string and write to new file
                        oldLine = line = origFile.readline()
                        if not line:
                            break

                        for datamaskWord in datamaskSpec:
                            line = re.sub(r'{0}'.format(datamaskWord), '__JADatamask__', line)

                        newFile.write(line)

                        if debugLevel > 3:
                            LogLine(
                                "DEBUG-4 JCDatamaskMaskFile() oldLine:|{0}\n, datamased line:|{1}|".format( oldLine, line ),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

                    origFile.close()
            except OSError as err:
                LogLine(
                    "ERROR JCDatamaskMaskFile() Can't open file:|{0}|, OSError:{1}".format( fileName, err ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
                returnStatus = False
            newFile.close()

    except OSError as err:
        LogLine(
            "ERROR JCDatamaskMaskFile() Can't write new file:|{0}|, OSError:{1}".format( newFileName, err ),
            interactiveMode,
            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
        returnStatus = False
    
    return returnStatus, newFileName

def JCComparePatterns(
        itemName,
        comparePatterns:dict, fileName:str, textBuffer:str,
        interactiveMode, debugLevel,
        myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType):
    """
    JCComparePatterns(
        itemName,
        comparePatterns, saveFileName,
        interactiveMode, debugLevel,
        myColors, colorIndex, outputFileHandle, HTMLBRTag, OSType)

    This function searches for a presence of compare patterns in line(s) within a file.
    If all patterns are found, returns True
    If any pattern is not found, returns False

    """
    returnStatus = True
    errorMsg = ''

    lines = ''
    ### text printed along with error message when pattern not found
    linesFileNameMsg = ''

    if fileName != None:
        try:
            with open( fileName, "r") as file:
                while True:
                    tempLine = file.readline()
                    if not tempLine:
                        break
                    lines += tempLine
                file.close()
                linesFileNameMsg = fileName
        except OSError as err:
            LogLine(
                "ERROR JCComparePatterns() item:{0}, can't open file:|{1}|, OSError:{2}".format(itemName, fileName, err ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
            returnStatus = False
    elif textBuffer != None:
        ### if textBuffer is list, make a multi-line string to be used for search later.
        if isinstance(textBuffer, list):
            for line in textBuffer:
                lines += (line + '\n')
        else:
            lines = textBuffer
        linesFileNameMsg = lines

    numberOfPatternsToFind = numberOfPatternsFound = 0
    if returnStatus == True:
        numberOfPatternsToFind = len(comparePatterns)
        
        ### search for each pattern in lineS   
        for comparePattern, conditions in comparePatterns.items():
            if debugLevel > 1:
                LogLine(
                    "DEBUG-2 JCComparePatterns() item:{0}, searching for ComparePattern:|{1}| in file or text:|{2}|".format( 
                        itemName, comparePattern, linesFileNameMsg ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
            myResults =  re.findall(r'{0}'.format(comparePattern), lines, re.MULTILINE)
            if len(myResults) > 0:
                numberOfMatchedPatterns = len(myResults[0])
                myResults = myResults[0]
            else:
                numberOfMatchedPatterns = 0
            if numberOfMatchedPatterns > 0:
                ### for group values matching to the patterns,
                ###    check conditions one by one in the conditions list
                ### group number spec uses index starting from 1, myResults[] index starts with 0
                conditionsMet = 0
                numberOfConditions = len(conditions)
                if debugLevel > 2:
                    LogLine(
                        "DEBUG-3 JCComparePatterns()\t\tcomparing expected group values:|{0}| to current group values:|{1}|".format( 
                            conditions, myResults ),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

                for findAllGroupNumber, compareValue in conditions.items():
                    if numberOfMatchedPatterns >= findAllGroupNumber:
                        try:
                            tempConditionsMet = False
                            if isinstance(compareValue,int) == True:
                                ### group number spec uses index starting from 1, myResults[] index starts with 0
                                ###   thus doing findAllGroupNumber-1 to pick up desired value from myResults
                                if int(myResults[findAllGroupNumber-1]) == int(compareValue):
                                    conditionsMet += 1
                                    tempConditionsMet = True
                            elif isinstance(compareValue,float) == True:
                                ### group number spec uses index starting from 1, myResults[] index starts with 0
                                ###   thus doing findAllGroupNumber-1 to pick up desired value from myResults
                                if float(myResults[findAllGroupNumber-1]) == float(compareValue):
                                    conditionsMet += 1
                                    tempConditionsMet = True
                            else:
                                ### group number spec uses index starting from 1, myResults[] index starts with 0
                                ###   thus doing findAllGroupNumber-1 to pick up desired value from myResults
                                if str(myResults[findAllGroupNumber-1]) == str(compareValue):
                                    conditionsMet += 1
                                    tempConditionsMet = True

                            if tempConditionsMet == True:
                                if debugLevel > 2:
                                    LogLine(
                                        "DEBUG-3 JCComparePatterns()\t\tregex group:{0}, expected value:|{1}| matched to current value:|{2}|".format( 
                                            findAllGroupNumber, compareValue, myResults[findAllGroupNumber-1] ),
                                        interactiveMode,
                                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
                            else:
                                LogLine(
                                    "ERROR JCComparePatterns() item:{0}, regex group:{1}, expected value:|{2}| is NOT matching to current value:|{3}| in the file or text:|{4}|".format( 
                                        itemName, findAllGroupNumber, compareValue, myResults[findAllGroupNumber-1], linesFileNameMsg ),
                                    interactiveMode,
                                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

                        except:
                            LogLine(
                                "ERROR JCComparePatterns() item:{0}, current value type conversion exception, regex group:{1}, expected value:|{2}| is NOT matching to current value:|{3}| in the file or text:|{4}| ".format( 
                                    itemName, findAllGroupNumber, compareValue, myResults[findAllGroupNumber-1], linesFileNameMsg ),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

                if conditionsMet == numberOfConditions:
                    ### all patterns found in current conditions
                    numberOfPatternsFound += 1
                else:
                    LogLine(
                        "ERROR JCComparePatterns() item:{0}, NOT all regex groups matched from the comparePattern:|{1}|, expected regex groups to match:{2}, regex groups matched:{3} in the file or text:|{4}|".format( 
                            itemName, comparePattern, numberOfConditions, conditionsMet, linesFileNameMsg ),
                        interactiveMode,
                        myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 

            else:
                LogLine(
                    "ERROR JCComparePatterns() item:{0}, comparePattern:|{1}| NOT found in file or text:|{2}|".format( 
                        itemName, comparePattern, linesFileNameMsg ),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
                    
            if numberOfPatternsToFind == numberOfPatternsFound:
                ### found all items, get out of the loop
                break

        if numberOfPatternsToFind != numberOfPatternsFound:
            LogLine(
                "ERROR  JCComparePatterns() item:{0}, ComparePatterns:|{1}|, expected pattern matches:{2}, actual pattern matches:{3} in the file or text:|{4}|".format(
                     itemName, comparePatterns, numberOfPatternsToFind, numberOfPatternsFound, linesFileNameMsg  ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType) 
            returnStatus = False

    return returnStatus, numberOfPatternsFound, (numberOfPatternsToFind-numberOfPatternsFound), errorMsg

def JCSetSystemVariables( defaultParameters, thisHostName, variables):
    """
    This function add system variables to variable dictionary.
    Variables added are:
        {{ JCSiteName }}
        {{ JCHostName }}
        {{ JCIPAddress }}
        {{ JCMACAddress }}
        {{ JCOSType }}
        {{ JCOSName }}
        {{ JCOSVersion }}
        {{ JCComponent }}

    """
    returnStatus = True
    errorMsg = ''
    variables['JCHostName'] = thisHostName
    variables['JCOSType'] = defaultParameters['OSType']
    variables['JCOSName'] = defaultParameters['OSName']
    variables['JCOSVersion'] = defaultParameters['OSVersion']
    variables['JCComponent'] = defaultParameters['Component']

    import uuid
    import socket
    variables['JCMACAddress'] = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    variables['JCIPAddress'] = socket.gethostbyname(thisHostName)

    """
    TBD Add code to handle multiple interface info 
    
    import psutil
    
    nics = psutil.net_if_addrs()
    for nic in nics.items():
        for name in nic:
            print("name:{0}".format(name))
    """

    return returnStatus, errorMsg

def JCIsSupportedCommand( paramValue:str, allowedCommands, OSType:str ):
    """
    JCGlobalLib.JAIsSupportedCommand( paramValue:str, allowedCommands, OSType:str )

    searches for the given command in allowed commands list
    If not found, returns False,
    If found, returns True
    """
    returnStatus = True

    errorMsg = ''

    ### first mask the contents inside '' and "" so that command separator characters
    ###  inside that string/word is not interpretted as command separators
    commands = re.sub(r'\'(.+)\'|\"(.+)\"', "__JAString__", paramValue)

    ### separate command words in param value. commands may be separated by ; or |
    commands = re.split(r';|\||&', commands)
    for command in commands:
        ## remove leading space if any
        command = command.lstrip()

        ### separate words
        commandWords = command.split()
        if len(commandWords) > 0:
            ### get first word from this command sentence
            command = commandWords[0]
        if OSType == "Windows":
            ### convert the command to lower case
            command = command.lower()
        if command not in allowedCommands:
            ### it is possible allowedCommands has options included to restrict commands like rpm to do "rpm -qa" only
            ###   search two words from command words
            if len(commandWords) > 1:
                twoWordsCommand = "{0} {1}".format(commandWords[0], commandWords[1])
                if twoWordsCommand not in allowedCommands:
                    ### look for commands inside (), search for contents inside the braket
                    ### this is to handle windows OS that supports commands like "(hostname).substring("
                    tempCommand =  re.search(r'\((.+)\)', command)
                    if tempCommand != None:
                        if tempCommand.group() not in allowedCommands:
                            returnStatus = False
                    else:
                        returnStatus = False
            else:
                returnStatus = False
            if returnStatus == False:
                    errorMsg += 'Unsupported command:|{0}|,'.format(command)
        
    return returnStatus,errorMsg

def JCParseVariables(
    environment:str, variableDefinitions:dict, overridePrevValue:bool, variables:dict,
    defaultParameters, allowedCommands, 
    interactiveMode:bool, debugLevel:int,
    myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine:bool, OSType:str ):
    
    """
    JCParseVariables(
    environment:str, variableDefinitions:dict, overridePrevValue:bool, variables:dict,
    defaultParameters, allowedCommands, 
    interactiveMode:bool, debugLevel:int,
    myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine:bool, OSType:str )

    This function processes the variable definitions, executes the commands, assigns the values to 
    variable dictionary

    Returns status, warnings, errors
    """
    returnStatus = True
    numberOfErrors = numberOfWarnings = 0

    ### expect variable definition to be in dict form
    for variableName, command in variableDefinitions.items():

        ### check for valid commands
        if JCIsSupportedCommand( command, allowedCommands, OSType):

            tempCommandToComputeVariableValue = os.path.expandvars( command ) 

            returnResult, returnOutput, errorMsg = JCExecuteCommand(
                                                defaultParameters['JCCommandShell'],
                                                tempCommandToComputeVariableValue, debugLevel, OSType)
            if returnResult == True:
                if len(returnOutput) > 0:
                    variableValue = returnOutput[0]
                else:
                    variableValue = ''
            else:
                LogLine(
                    "ERROR JCParseVariables() Not able to compute variable value for environment:{0}, variable name:{1}, command:{2}, error:{3}".format(
                        environment, variableName, command, errorMsg),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

                variableValue = 'Error'

            if overridePrevValue == True:
                ### even if prev value present, override it to use current environment spec
                variables[variableName] = variableValue
            else:                
                if variableName not in variables:
                    ### value not defined yet, assign it
                    variables[variableName] = variableValue

            if debugLevel > 1:
                LogLine(
                    "DEBUG-2 JCParseVariables() environment:{0}, variable name:{1}, command:{2}, value:{3}".format(
                        environment, variableName, command, variableValue),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
        else:
            ### not a valid command, log WARNing
            LogLine(
                "WARN JCParseVariables() Unsupported command, environment:{0}, variable name:{1}, command:{2}".format(
                    environment, variableName, command),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)
            numberOfWarnings += 1

    if debugLevel > 0:
        LogLine(
            "DEBUG-1 JCParseVariables() environment:{0}, number of variables parsed:{1}, with warnings:{2}, and errors:{3}".format(
                environment, len(variables), numberOfWarnings, numberOfErrors),
            interactiveMode,
            myColors, colorIndex, outputFileHandle, HTMLBRTag, False, OSType)

    return returnStatus, numberOfWarnings, numberOfErrors

def JCSubstituteVariableValues( variables, attributeValue):
    """
    This function replaces variable occurence with variable value in given attributeValue string
    Variable is of the form {{ varName }}
    attributeValue can have more than one variable

    Return True if at least one variable replaced,
            False, if no variable found

    """
    returnStatus = False

    ### attributeValue may have variable in the form '{{ varName }}'
    ### replace any variable name with variable value
    variableNames = re.findall(r'\{\{ (\w+) \}\}', attributeValue)
    if len(variableNames) > 0:
        ### replace each variable name with variable value
        for variableName in variableNames:
            if variableName in variables:
                if variables[variableName] != None:
                    replaceString = '{{ ' + variableName + ' }}'
                    attributeValue = attributeValue.replace(replaceString, variables[variableName])
                    returnStatus = True

    return returnStatus, attributeValue

def JCEvaluateComparePatternGroupValues(
    objectName:str, paramValue:dict, variables:dict,
    interactiveMode:bool, debugLevel:int,
    myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine:bool, OSType:str ):

    returnStatus = True

    ### for condition list associated with each compare pattern,
    ###    check whether the group value field has variable name.
    ###    If yes, replace that variable name with current variable value
    ###         so that current environment value is compared to this variable value based on environment 
    for comparePattern, conditions in paramValue.items():
        if debugLevel > 2:
            LogLine(
                "DEBUG-3 JCReadConfigCompare() processing ComparePattern:|{0}| of item:|{1}|".format( 
                    comparePattern, objectName ),
                interactiveMode,
                myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType) 

        for findAllGroupNumber, compareValue in conditions.items():
            if debugLevel > 2:
                LogLine(
                    "DEBUG-3 JCReadConfigCompare() \tprocessing match definition of group:{0}, groupValue:|{1}|".format( 
                            findAllGroupNumber, compareValue),
                    interactiveMode,
                    myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType) 

            if isinstance( compareValue, str) == True:
                ### expected group value may have variable in the form '${{ varName }}' 
                ### replace any variable name with variable value
                variableNames = re.findall(r'\{\{ (\w+) \}\}', compareValue)
                if len(variableNames) > 0:
                    if debugLevel > 2:
                        LogLine(
                            "DEBUG-3 JCReadConfigCompare() \t\tprocessing group value variable(s):|{0}|".format( 
                                variableNames),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType) 

                    originalCompareValue = compareValue
                    ### replace each variable name with variable value
                    for variableName in variableNames:
                        if variableName in variables:
                            replaceString = '{{ ' + variableName + ' }}'
                            try:
                                compareValue = compareValue.replace(replaceString, variables[variableName])
                            except:
                                LogLine(
                                    "DEBUG-3 JCReadConfigCompare() \t\texception while replacing variable:|{0}| with variable value:|{1}|, condition:|{2}|, ComparePatterns:|{3}|, item:|{4}|".format( 
                                        compareValue, replaceString, conditions, paramValue, objectName),
                                    interactiveMode,
                                    myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType) 

                        else:
                            LogLine(
                                "WARN JCReadConfigCompare() Unknown variable:{0} seen, Item Name:|{1}|, ComparePatterns:|{2}|, conditions:|{3}|, group:{4}, groupValue:|{5}|".format(
                                    variableName, objectName, comparePattern, conditions, findAllGroupNumber, compareValue),
                                interactiveMode,
                                myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType)
                            numberOfWarnings += 1
                    if debugLevel > 2:
                        LogLine(
                            "DEBUG-3 JCReadConfigCompare() Item Name:|{0}|, original compare value:|{1}|, compare value after substituting the variable values:|{2}|".format(
                                objectName, originalCompareValue, compareValue),
                            interactiveMode,
                            myColors, colorIndex, outputFileHandle, HTMLBRTag, diffLine, OSType)
                            
                    ### assign the value back to conditions list
                    paramValue[comparePattern][findAllGroupNumber] =  compareValue
                    
    return returnStatus


    """
    This function prints enitre file if pattern is not passed
    If pattern is passed, searches for the last occurrence of that pattern and displays lines after that till end of the file

    Returns True on success, False on failure along with errorMsg

    """
    returnStatus = True
    errorMsg = ''
    buffer = []
    patternFound = False
    if pattern == None or pattern == '':
        searchForPattern = False
    else:
        searchForPattern = True
        searchPattern = r"{0}".format(pattern)
        
    try:
        with open( fileName, "r") as reportFile:
            print("\nFileName: {0}\n".format(fileName))
            while True:
                line = reportFile.readline()
                if not line:
                    break
                line = line.rstrip()
                if searchForPattern == True:
                    if re.search(searchPattern, line):
                        buffer = []  
                        buffer.append(line)  
                        patternFound = True
                    elif patternFound == True:
                        buffer.append(line) 
                else:
                    print( "{0}".format(line))
            reportFile.close()

            if patternFound == True:
                for line in buffer:
                    print( "{0}".format(line))    
    except OSError as err:
        errorMsg = "ERROR could not open the file:{0}, errorMsg:{1}".format( fileName, err)
        returnStatus = False

    return returnStatus, errorMsg