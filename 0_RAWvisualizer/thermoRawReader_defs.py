#Program: thermoRawReader_functions
#Author(s): David Helminiak
#Date Created: June 2019
#Date Last Modified: Semptember 2019
#==================================================================

#==================================================================
#ADDITIONAL NOTES:
#==================================================================
#Proposed structure converted from golang unthermo project
#https://bitbucket.org/proteinspector/ms/src/master/unthermo/reader.go
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
import binascii
import struct
import sys
import numpy as np
import datetime
#==================================================================

#==================================================================
#CLASS/OBJECT DEFINITIONS
#==================================================================
class Header():
    def __init__(self, fileSTR, filePointer):
        self.filePointer = filePointer
        self.magicNum, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer)
        self.signature, self.filePointer = convert('schar', 18, fileSTR, self.filePointer)
        self.unknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown3, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown4, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.version, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.auditStartTimeStamp, self.filePointer = convert('timeStamp', 8, fileSTR, self.filePointer)
        self.startAuditTag1, self.filePointer = convert('schar', 50, fileSTR, self.filePointer)
        self.startAuditTag2, self.filePointer = convert('schar', 50, fileSTR, self.filePointer)
        self.startAuditUnknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.auditStopTimeStamp, self.filePointer = convert('timeStamp', 8, fileSTR, self.filePointer)
        self.stopAuditTag1, self.filePointer = convert('schar', 50, fileSTR, self.filePointer)
        self.stopAuditTag2, self.filePointer = convert('schar', 50, fileSTR, self.filePointer)
        self.stopAuitUnknown1, self.filePointer = convert('int', 4, fileSTR, self.filePointer)
        self.unknown5, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown6, self.filePointer = convert('schar', 60, fileSTR, self.filePointer)
        self.headerTag, self.filePointer = convert('schar', 1028, fileSTR, self.filePointer)

class InfoPreamble():
    def __init__(self, fileSTR, filePointer, header):
        self.filePointer = filePointer
        self.methodFilePresent, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
        self.year, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer)
        self.month, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.weekday, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.day, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.hour, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.minute, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.second, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 
        self.millisecond, self.filePointer = convert('ushort', 2, fileSTR, self.filePointer) 

        if header.version >= 57:
            self.unknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
            self.dataAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
            self.nControllers, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
            self.nControllers2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
            self.unknown2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer) 
            self.unknown3, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            if header.version < 64:
                self.RunHeaderAddr32 = []
                self.unknown4 = []
                self.unknown5 = []
                for self.nControllerNum in range(0,self.nControllers):
                    self.result, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
                    self.RunHeaderAddr32.append(self.result)
                    self.result, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
                    self.unknown4.append(self.result)
                    self.result, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
                    self.unknown5.append(self.result)
                self.RunHeaderAddr = np.multiply(self.RunHeaderAddr32,2).tolist() #Conversion for uint64
                if header.version == 57:
                    self.padding1 = fileSTR[self.filePointer:self.filePointer+((756-12*self.nControllers)*2)]
                    self.filePointer = self.filePointer+((756-12*self.nControllers)*2)
                else:
                    self.padding1 = fileSTR[self.filePointer:self.filePointer+((760-12*self.nControllers)*2)]
                    self.filePointer = self.filePointer+((760-12*self.nControllers)*2)
            else:
                self.padding1 = fileSTR[self.filePointer:self.filePointer+(764*2)]
                self.filePointer = self.filePointer+(764*2)

        if header.version >= 64:
            self.dataAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.unknown6, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.runHeaderAddr = []
            self.unknown7 = []
            for self.nControllerNum in range(0,nControllers):
                self.result, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
                self.runHeaderAddr.append(self.result)
                self.result, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
                self.unknown7.append(self.result)
            #No conversion to uint64?
            if header.version < 66:
                self.padding2 = fileSTR[self.filePointer:self.filePointer+(self.filePointer+1016-16*self.nControllers)]
                self.filePointer = self.filePointer+1016-16*self.nControllers
            else:
                padding2 = fileSTR[self.filePointer:self.filePointer+(self.filePointer+1032-16*self.nControllers)]
                self.filePointer = self.filePointer+1032-16*self.nControllers   

class InjectionData():
    def __init__(self, fileSTR, filePointer):
        self.filePointer = filePointer
        self.unknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.rowNumber, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.vial, self.filePointer = convert('schar', 12, fileSTR, self.filePointer)
        self.injectionVolume, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.sampleWeight, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.sampleVolume, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.internationalStandardAmount, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.dilutionFactor, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        
class SequencerRow():
    def __init__(self, fileSTR, filePointer, header):
        self.filePointer = filePointer
        self.injectionData = InjectionData(fileSTR, self.filePointer)
        self.filePointer = self.injectionData.filePointer
        self.unknown1, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.unknown2, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.iden, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.comment, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.userLabel1, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.userLabel2, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.userLabel3, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.userLabel4, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.userLabel5, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.instMethod, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.procMethod, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.fileName, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.path, self.filePointer = readPascalString(fileSTR, self.filePointer)

        if header.version >= 57:
            self.vial, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown3, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown4, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown5, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        if header.version >= 60:
            self.unknown6, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown7, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown8, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown9, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown10, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown11, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown12, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown13, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown14, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown15, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown16, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown17, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown18, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown19, self.filePointer = readPascalString(fileSTR, self.filePointer)
            self.unknown20, self.filePointer = readPascalString(fileSTR, self.filePointer)

class AutoSamplerInfo():
    def __init__(self, fileSTR, filePointer):
        self.filePointer = filePointer
        self.unknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.numberOfWells, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown3, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown4, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown5, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)  
        self.text, self.filePointer = readPascalString(fileSTR, self.filePointer)

class FileInformation():
    def __init__(self, fileSTR, filePointer, header):
        self.filePointer = filePointer
        self.infoPreamble = InfoPreamble(fileSTR, self.filePointer, header)
        self.filePointer = self.infoPreamble.filePointer
        self.heading1, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.heading2, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.heading3, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.heading4, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.heading5, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.unknown1, self.filePointer = readPascalString(fileSTR, self.filePointer)

class SampleInfo():
    def __init__(self, fileSTR, filePointer):
        self.filePointer = filePointer
        self.unknown1, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown2, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.firstScanNumber, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.lastScanNumber, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.instlogLength, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown3, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown4, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.scanIndexAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.dataAdd32r, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.instlogAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.errorlogAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown5, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.maxSignal, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.lowmz, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.highmz, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.startTime, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.endTime, self.filePointer = convert('double', 8, fileSTR, self.filePointer) 
        self.unknown6 = fileSTR[self.filePointer:self.filePointer+112]
        self.filePointer = self.filePointer+112
        self.tag1, self.filePointer = convert('schar', 88, fileSTR, self.filePointer)
        self.tag2, self.filePointer = convert('schar', 40, fileSTR, self.filePointer)
        self.tag3, self.filePointer = convert('schar', 320, fileSTR, self.filePointer)
        
class RunHeader():
    def __init__(self, fileSTR, filePointer, header, fileInformation):
        self.filePointer = filePointer
        self.sampleInfo = SampleInfo(fileSTR, self.filePointer)
        self.filePointer = self.sampleInfo.filePointer
        self.filename1, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename2, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename3, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename4, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename5, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename6, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.unknown1, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.unknown2, self.filePointer = convert('double', 8, fileSTR, self.filePointer)
        self.filename7, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename8, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename9, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename10, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename11, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename12, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.filename13, self.filePointer = convert('schar', 520, fileSTR, self.filePointer)
        self.scantrailerAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.scanparamsAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown3, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown4, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.nsegs, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown5, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown6, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.ownAddr32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown7, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.unknown8, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)

        #uint64 adjustment
        self.scanIndexAddr = self.sampleInfo.scanIndexAddr32*2
        self.dataAddr = fileInformation.infoPreamble.dataAddr32*2
        self.instlogAddr = self.sampleInfo.instlogAddr32*2
        self.errorlogAddr = self.sampleInfo.errorlogAddr32*2
        self.scantrailerAddr = self.scantrailerAddr32*2
        self.scanparamsAddr = self.scanparamsAddr32*2
        self.ownAddr = self.ownAddr32*2

        if header.version >= 64:
            self.scanindexaddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.dataAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.instlogAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.errorlogAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.unknown9, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.scantrailerAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.scanparamsAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.unknown10, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown11, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.ownAddr, self.filePointer = convert('ulonglong', 8, fileSTR, self.filePointer)
            self.unknown12, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown13, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown14, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown15, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown16, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown17, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown18, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown19, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown20, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown21, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown22, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown23, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown24, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown25, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown26, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown27, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown28, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown29, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown30, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown31, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown32, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown33, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown34, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
            self.unknown35, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)

        self.unknown36 = fileSTR[self.filePointer:self.filePointer+16]
        self.filePointer = self.filePointer+16
        self.unknown37, self.filePointer = convert('uint', 4, fileSTR, self.filePointer)
        self.device, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.model, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.sn, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.swVer, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.tag1, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.tag2, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.tag3, self.filePointer = readPascalString(fileSTR, self.filePointer)
        self.tag4, self.filePointer = readPascalString(fileSTR, self.filePointer)
        
class ScanIndex():
    def __init__(self, indexInfo, indexPointer, header, dataAddr):
        self.indexPointer = indexPointer
        if header.version == 66:
            sys.exit('Error! - Code for this version uncertain.')
        elif header.version == 64:
            self.offset32, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.index, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.scanEvent, self.indexPointer = convert('ushort', 2, indexInfo, self.indexPointer)
            self.scanSegment, self.indexPointer = convert('ushort', 2, indexInfo, self.indexPointer)
            self.next, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.unknown1, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.dataPacketSize, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.time, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.totalCurrent, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.baseIntensity, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.basemz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.lowmz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.highmz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.offset, self.indexPointer = convert('ulonglong', 8, indexInfo, self.indexPointer)
            self.offset += dataAddr #Adjust pointer address to be absolute
        else:
            self.offset32, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.index, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.scanEvent, self.indexPointer = convert('ushort', 2, indexInfo, self.indexPointer)
            self.scanSegment, self.indexPointer = convert('ushort', 2, indexInfo, self.indexPointer)
            self.next, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.unknown1, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.dataPacketSize, self.indexPointer = convert('uint', 4, indexInfo, self.indexPointer)
            self.time, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.totalCurrent, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.baseIntensity, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.basemz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.lowmz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.highmz, self.indexPointer = convert('double', 8, indexInfo, self.indexPointer)
            self.offset = self.offset32*2 #Conversion for uint64
            self.offset += dataAddr #Adjust pointer address to be absolute

class Reaction():
    def __init__(self, eventInfo, eventPointer):
        self.eventPointer = eventPointer
        self.precursormz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
        self.unknown1, self.eventPointer = convert('double', 8, eventInfo, eventPointer)
        self.energy, self.eventPointer = convert('double', 8, eventInfo, eventPointer)
        self.unknown2, self.eventPointer = convert('uint', 4, eventInfo, eventPointer)
        self.unknown3, self.eventPointer = convert('uint', 4, eventInfo, eventPointer)

class ScanEvent():
    def __init__(self, eventInfo, eventPointer, header):
        self.eventPointer = eventPointer
        self.unknown1 = []
        self.unknown2 = []
        self.mzRange = []
        if header.version < 66:
            if header.version < 57:
                self.dataPreamble = eventInfo[self.eventPointer:self.eventPointer+82]
                self.eventPointer = self.eventPointer+82
            elif header.version >= 57 and header.version < 62:
                self.dataPreamble = eventInfo[self.eventPointer:self.eventPointer+160]
                self.eventPointer = self.eventPointer+160
            elif header.version >= 62 and header.version < 63:
                self.dataPreamble = eventInfo[self.eventPointer:self.eventPointer+240]
                self.eventPointer = self.eventPointer+240
            elif header.version >= 63:
                self.dataPreamble = eventInfo[self.eventPointer:self.eventPointer+256]
                self.eventPointer = self.eventPointer+256
            self.nPrecursors, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.reactions = []
            for nPrecursorNum in range(0, self.nPrecursors):
                self.reaction = Reaction(eventInfo, self.eventPointer)
                self.eventPointer = self.reaction.eventPointer
                self.reactions.append(self.reaction)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
            self.lowmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            self.highmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            self.mzRange.append(FractionCollector(self.lowmz, self.highmz))
            self.nParam, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            if self.nParam == 4:
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.a, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.b, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.c, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            elif self.nParam == 7:
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.a, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.b, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.c, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
        else: #version 66
            self.dataPreamble, self.eventPointer = convert('uchar', 132, eventInfo, self.eventPointer)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)    
            self.nPrecursors, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)

            if self.dataPreamble[10] == 1: #ms2 (dependent scan)
                self.reactions = []
                for self.nPrecursorNum in range(0, self.nPrecursors):
                    self.reaction = Reaction(eventInfo, self.eventPointer)
                    self.eventPointer = reaction.eventPointer
                    self.reactions.append(self.reaction)
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.value, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.unknown2.append(self.value)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.lowmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.highmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.mzRange.append(FractionCollector(self.lowmz, self.highmz))
                self.nParam, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            else: #ms1
                self.lowmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.highmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.mzRange.append(FractionCollector(self.lowmz, self.highmz))
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.lowmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.highmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.mzRange.append(FractionCollector(self.lowmz, self.highmz))
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
                self.unknown1.append(self.value)
                self.lowmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.highmz, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
                self.mzRange.append(FractionCollector(self.lowmz, self.highmz))
                self.nParam, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown2.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown2.append(self.value)
            self.a, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            self.b, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            self.c, self.eventPointer = convert('double', 8, eventInfo, self.eventPointer)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)
            self.unknown1.append(self.value)
            self.value, self.eventPointer = convert('uint', 4, eventInfo, self.eventPointer)

class Chunk:
    def __init__(self, scanData, dataPointer, layout):
        self.dataPointer = dataPointer
        self.firstBin, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.nBins, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.fudge = None
        if layout > 0:
            self.fudge, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
        self.signal = []
        for self.binNum in range(0, self.nBins):
            self.value, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
            self.signal.append(self.value)

class ScanDataPacket:
    def __init__(self, fileSTR, scanIndexes, scanNum):
        scanData = fileSTR[scanIndexes[scanNum].offset:scanIndexes[scanNum].offset+(scanIndexes[scanNum].dataPacketSize*2)]
        self.dataPointer = 0
        self.unknown1, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.profileSize, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.peaklistSize, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.layout, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.descriptorListSize, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.unknownStreamSize, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.tripletStreamSize, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.unknown2, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
        self.lowmz, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
        self.highmz, self.dataPointer = convert('float', 4, scanData, self.dataPointer)

        if self.profileSize > 0:
            self.firstValue, self.dataPointer = convert('double', 8, scanData, self.dataPointer)
            self.step, self.dataPointer = convert('double', 8, scanData, self.dataPointer)
            self.peakCount, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
            self.nBins, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
            self.chunks = []
            for self.peakNum in range(0, self.peakCount):
                self.chunk = Chunk(scanData, self.dataPointer, self.layout)
                self.dataPointer = self.chunk.dataPointer
                self.chunks.append(self.chunk)
        if self.peaklistSize > 0:
            self.count, self.dataPointer = convert('uint', 4, scanData, self.dataPointer)
            self.centroidedPeaks = []
            for self.countNum in range(0,self.count):
                self.centroidedPeak = CentroidedPeak(scanData, self.dataPointer)
                self.dataPointer = self.centroidedPeak.dataPointer
                self.centroidedPeaks.append(self.centroidedPeak)
        self.peakDescriptors = []
        for self.descriptorListNum in range(0,self.descriptorListSize):
            self.peakDescriptor = PeakDescriptor(scanData, self.dataPointer)
            self.dataPointer = self.peakDescriptor.dataPointer
            self.peakDescriptors.append(self.peakDescriptor)
        self.unknown = []
        for self.unknownNum in range(0,self.unknownStreamSize):
            self.unknownValue, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
            self.unknown.append(self.unknownValue)
        self.triplets = []
        for self.tripletNum in range(0,self.tripletStreamSize):
            self.triplet, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
            self.triplets.append(self.triplet)

class FractionCollector():
    def __init__(self, lowmz, highmz):
        self.lowmz = lowmz
        self.highmz = highmz

class CentroidedPeak:
    def __init__(self, scanData, dataPointer):
        self.dataPointer = dataPointer
        self.mz, self.dataPointer = convert('float', 4, scanData, self.dataPointer)
        self.abundance, self.dataPointer = convert('float', 4, scanData, self.dataPointer)

class PeakDescriptor:
    def __init__(self, scanData, dataPointer):
        self.dataPointer = dataPointer
        self.index, self.dataPointer = convert('ushort', 2, scanData, self.dataPointer)
        self.flags, self.dataPointer = convert('uchar', 1, scanData, self.dataPointer)
        self.charge, self.dataPointer = convert('uchar', 1, scanData, self.dataPointer)

class Scan():
    def __init__(self, mzValues, signalValues):
        self.mzValues = mzValues
        self.signalValues = signalValues

class PascalString():
    def __init__(self):
        self.length = None
        self.text = None

#==================================================================
#FUNCTION DEFINITIONS
#==================================================================
def readPascalString(fileSTR, filePointer):
    length, filePointer = convert('int', 4, fileSTR, filePointer)
    information, filePointer = convert('schar', length*2, fileSTR, filePointer)
    return information, filePointer

#Convert encoded hex information into a user readable format
def convert(cType, numBytes, fileSTR, filePointer):
    stringFlag = False #Does the result require string fomrating; Default
    padFlag = False
    #Setup various types for conversion; Several of these combinations remain untested!
    if cType == 'char': fmtSuf = 'c'; fmtSize = 1; stringFlag = True
    elif cType == 'schar': fmtSuf = 'b'; fmtSize = 1; stringFlag = True
    elif cType == 'uchar': fmtSuf = 'B'; fmtSize = 1;
    elif cType == 'bool': fmtSuf = '?'; fmtSize = 1;
    elif cType == 'short': fmtSuf = 'h'; fmtSize = 2;
    elif cType == 'ushort': fmtSuf = 'H'; fmtSize = 2;
    elif cType == 'int': fmtSuf = 'i'; fmtSize = 4;
    elif cType == 'uint': fmtSuf = 'I'; fmtSize = 4;
    elif cType == 'long': fmtSuf = 'l'; fmtSize = 4;
    elif cType == 'ulong': fmtSuf = 'L'; fmtSize = 4;
    elif cType == 'longlong': fmtSuf = 'q'; fmtSize = 8;
    elif cType == 'ulonglong': fmtSuf = 'Q'; fmtSize = 8;
    elif cType == 'float': fmtSuf = 'f'; fmtSize = 4;
    elif cType == 'double': fmtSuf = 'd'; fmtSize = 8;
    elif cType == 'paduint': fmtSuf = 'I'; fmtSize = 2; padFlag = True; padding = b'\x00\x00'
    elif cType == 'timeStamp': fmtSuf = 'Q'; fmtSize = 8
    else: sys.exit('Error! - Type specified not defined in function definition for: convert')
        
    #Determine the structure format and end file pointer location
    fmt = '<' + str(int(numBytes/fmtSize)) + fmtSuf
    filePointerEnd = filePointer + (numBytes*2)
    
    #Return extracted data and updated file pointer location
    if cType == 'timeStamp':  
        dt = struct.unpack('<Q', binascii.unhexlify(fileSTR[filePointer:filePointer+16]))[0]
        seconds, microseconds = divmod(dt/10, 1e6)
        days, seconds = divmod(seconds, 86400)
        datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds)
        return str(datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds)), filePointerEnd
    
    if not stringFlag: 
        if not padFlag:
            return struct.unpack(fmt, binascii.unhexlify(fileSTR[filePointer:filePointerEnd]))[0], filePointerEnd
        else:
            return struct.unpack('<I', (binascii.unhexlify(fileSTR[filePointer:filePointerEnd])+padding))[0], filePointerEnd
    else:
        #Join the characters together after converting them from int to char
        return ''.join(np.char.mod('%c', struct.unpack(fmt, binascii.unhexlify(fileSTR[filePointer:filePointerEnd])))), filePointerEnd

