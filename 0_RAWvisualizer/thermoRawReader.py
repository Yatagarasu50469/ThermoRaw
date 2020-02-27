#==================================================================
#Program: thermoRawReader
#Author(s): David Helminiak
#Date Created: June 2019
#Date Last Modified: September 2019
#Version 1.0
#Changelog: 0.1  - Transition from golang unthermo project
#           0.2  - Validation of version 63 .RAW file spectra
#           1.0  - Initial release
#==================================================================

#=================================================================
#FAQ
#==================================================================
#MY RAW VERSION REPORTS AS INCOMPATABLE
#Program may work on .RAW files other than v63, but they have not
#yet been validated. To test, add file format number to the
#suppotedVersions variable temporarily. Whether successful, or
#otherwise please submit an issue report so that the relevent
#individuals might be informed. Thank you.

#MY DESIRED DATA ISN'T OUTPUT BY THE FUNCTION(S) PROVIDED?
#At the time of code's construction, the only desired information
#was the spectra contained within v63 .RAW files, though other
#data is obtained in the process of doing so. Feel free to
#contribute additional functions through a pull request!

#HELP, MY DATA ISN'T WORKING
#Please submit an issue report and include a .RAW file that isn't
#working. Note that there are no guarantees that it will be looked
#at, but more information is always useful!
#==================================================================

#=================================================================
#OPERATION EXAMPLE(S)
#==================================================================
#Intended for use inside of a python3 environment:

#READING:
#from thermoRawReader import thermoRAW_spectra
#spectra = thermoRAW_spectra('20161022-PFA-104-1-1-line1.RAW')
#mzValuesFirstPixel = spectra[0].mzValues
#signalValuesFirstPixel = spectra[0].signalValues

#PLOTTING
#import matplotlib.pyplot as plt
#scanNum = 0
#plt.plot(spectra[scanNum].mzValues,spectra[scanNum].signalValues)
#==================================================================

#==================================================================
#ADDITIONAL NOTES:
#==================================================================
#REFERENCE(S)
#Proposed structure converted from golang unthermo project
#https://bitbucket.org/proteinspector/ms/src/master/unthermo/reader.go

#TYPICAL MATCHED VARIABLE CONVERSIONS FROM GOLANG
#For use in the convert function
#uint8 = uchar 1
#uint16 = ushort 2
#uint32 = uint 4
#int32 = int 4
#float32 = float 4
#float64 = double 8 
#==================================================================

#==================================================================
#LIBRARY IMPORTS
#==================================================================
from thermoRawReader_defs import *
import binascii
#==================================================================

#STATIC GLOBAL PARAMETERS
#=================================
#List of validated .RAW file formats, others not yet tested
supportedVersions = [63]


#MAIN PROGRAMS
#==================================================================
#Read a thermo .RAW file and return included spectrua
#Returns array of spectrums with the following data:
#     mzValues[]
#     signalValues[]
def thermoRAW_spectra(RAW_fileNAME):
    #Read in the .RAW file specified as a single string
    file = []
    with open(RAW_fileNAME, 'rb') as infile:
        while True:
            data = infile.read(1024) #Read in a block
            if not data: break
            file.append(binascii.hexlify(data).decode('utf-8'))
    fileSTR = ''.join(file)

    #Obtain file header
    header = Header(fileSTR, 0)
    filePointer = header.filePointer

    #Verify that this file can theoretically be scanned
    if header.version not in supportedVersions:
        sys.exit('Error! - .RAW version is not supported by this script')
    if header.signature != 'Finnigan':
        sys.exit('Error! - File signature does not match expected value, suggesting an incorrect input file format')

    #Gather general file and pointer information
    sequencerRow = SequencerRow(fileSTR, filePointer, header)
    filePointer = sequencerRow.filePointer
    autoSamplerInfo = AutoSamplerInfo(fileSTR, filePointer)
    filePointer = autoSamplerInfo.filePointer
    fileInformation = FileInformation(fileSTR, filePointer, header)
    filePointer = fileInformation.filePointer

    #Read available scan headers until an MS header is detected
    scantrailerAddr = 0
    for i in range(0,len(fileInformation.infoPreamble.RunHeaderAddr)):
        if scantrailerAddr != 0: break
        runHeader = RunHeader(fileSTR, int(fileInformation.infoPreamble.RunHeaderAddr[i]), header, fileInformation)
        filePointer = runHeader.filePointer
        scantrailerAddr = runHeader.scantrailerAddr
    if scantrailerAddr == 0:
        sys.exit("Error! - No MS header detected in the file")

    #Obtain actual scan data
    scanEvents = []
    scanIndexes = []
    eventInfo = fileSTR[runHeader.scantrailerAddr+8:runHeader.scanparamsAddr]
    indexInfo = fileSTR[runHeader.scanIndexAddr:runHeader.scantrailerAddr]
    eventPointer = 0
    indexPointer = 0

    nScans = runHeader.sampleInfo.lastScanNumber - runHeader.sampleInfo.firstScanNumber + 1
    for scanNum in range(0, nScans):
        scanEvent = ScanEvent(eventInfo, eventPointer, header)
        scanIndex = ScanIndex(indexInfo, indexPointer, header, runHeader.dataAddr)
        eventPointer = scanEvent.eventPointer
        indexPointer = scanIndex.indexPointer
        scanEvents.append(scanEvent)
        scanIndexes.append(scanIndex)

    #Extract actual usuable values from the scan data
    scans = []
    for scanNum in range(0,nScans):
        ##Version 66 information?
        #time = scanIndexes[scanNum].time
        #preamble = scanEvents[scanNum].dataPreamble
        #preamblePointer = 0
        #preambleExt = []
        # while preamblePointer < len(preamble):
        #     value, preamblePointer = convert('uchar', 1, preamble, preamblePointer)
        #     preambleExt.append(value)
        # msLevel = preambleExt[6]
        # analyzer = preambleExt[40]
        # precursormzs = []
        # for i in range(0, len(scanEvents[scanNum].reactions)):
        #     precursormzs.append(scanEvents[scanNum].reactions[i].precursormz)
        scanDataPacket = ScanDataPacket(fileSTR, scanIndexes, scanNum)
        mzValues = []
        signalValues = []
        if scanDataPacket.peakCount <= 0:
            for i in range(0, scanDataPacket.count):
                mzValues.append(scanDataPacket.centroidedPeaks[i].mz)
                signalValues.append(scanDataPacket.centroidedPeak[i].abundance)
        else:
            scanEvent = scanEvents[scanNum]
            nParam = scanEvent.nParam
            for i in range(0, scanDataPacket.peakCount):
                for j in range(0, scanDataPacket.chunks[i].nBins):
                    v = (scanDataPacket.firstValue+((scanDataPacket.chunks[i].firstBin+j)*scanDataPacket.step)) + (scanDataPacket.chunks[i].fudge)
                    if nParam == 4:
                        mzValue = scanEvent.a+scanEvent.b/v+scanEvent.c/v/v
                    elif nParam == 5 or nParam == 7:
                        mzValue = scanEvent.a+scanEvent.b/v/v+scanEvent.c/v/v/v/v
                    else:
                        mzValue = v
                    mzValues.append(mzValue)
                    signalValues.append(scanDataPacket.chunks[i].signal[j])
        scans.append(Scan(mzValues, signalValues))
    return scans, scanIndexes



