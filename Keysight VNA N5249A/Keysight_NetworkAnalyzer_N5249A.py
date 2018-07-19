#!/usr/bin/env python

import InstrumentDriver
from VISA_Driver import VISA_Driver
from InstrumentConfig import InstrumentQuantity
import numpy as np

__version__ = "0.0.1"

class Error(Exception):
    pass

class Driver(VISA_Driver):
    """ This class implements the Agilent 5230 PNA driver"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # init meas param dict
        self.dMeasParam = {}
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)
        # do perform get value for acquisition mode


    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""
        # update visa commands for triggers
        if quant.name in ('S11 - Enabled', 'S21 - Enabled', 'S31 - Enabled', 'S41 - Enabled','S22 - Enabled' ,'S12 - Enabled','S32 - Enabled','S42 - Enabled','S33 - Enabled','S13 - Enabled','S23 - Enabled','S43 - Enabled','S44 - Enabled','S14 - Enabled','S24 - Enabled','S34 - Enabled'):
            if self.getModel() in ('E5071C'):
                # new trace handling, use trace numbers, set all at once
                lParam = ['S11', 'S21', 'S31','S41','S22','S12','S32','S42','S33','S13','S23','S43','S44','S14','S24','S34']
                dParamValue = dict()
                for param in lParam:
                    dParamValue[param] = self.getValue('%s - Enabled' % param)
                dParamValue[quant.name[:3]] = value
                # add parameters, if enabled
                self.dMeasParam = dict()
                for (param, enabled) in dParamValue.items():
                    if enabled:
                        nParam = len(self.dMeasParam)+1
                        self.writeAndLog(":CALC:PAR%d:DEF %s" %
                                         (nParam, param))
                        self.dMeasParam[param] = nParam
                # set number of visible traces
                self.writeAndLog(":CALC:PAR:COUN %d" % len(self.dMeasParam))
            else:
                # get updated list of measurements in use
                self.getActiveMeasurements()
                param = quant.name[:3]
                # old-type handling of traces
                if param in self.dMeasParam:
                    # clear old measurements for this parameter
                    for name in self.dMeasParam[param]:
                        self.writeAndLog("CALC:PAR:DEL '%s'" % name)
                # create new measurement, if enabled is true
                if value:
                    newName = 'LabC_%s' % param
                    self.writeAndLog("CALC:PAR:EXT '%s','%s'" % (newName, param))
                    # show on PNA screen
                    iTrace = 1 + ['S11', 'S21', 'S31','S41','S22','S12','S32','S42','S33','S13','S23','S43','S44','S14','S24','S34'].index(param)
    #                sPrev = self.askAndLog('DISP:WIND:CAT?')
    #                if sPrev.find('EMPTY')>0:
    #                    # no previous traces
    #                    iTrace = 1
    #                else:
    #                    # previous traces, add new
    #                    lTrace = sPrev[1:-1].split(',')
    #                    iTrace = int(lTrace[-1]) + 1
                    self.writeAndLog("DISP:WIND:TRAC%d:FEED '%s'" % (iTrace, newName))
                    # add to dict with list of measurements
                    self.dMeasParam[param] = [newName]
        elif quant.name in ('Wait for new trace',):
            # do nothing
            pass
        else:
            # run standard VISA case
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)
        return value


    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        # check type of quantity
        if quant.name in ('S11 - Enabled', 'S21 - Enabled', 'S31 - Enabled', 'S41 - Enabled','S22 - Enabled' ,'S12 - Enabled','S32 - Enabled','S42 - Enabled','S33 - Enabled','S13 - Enabled','S23 - Enabled','S43 - Enabled','S44 - Enabled','S14 - Enabled','S24 - Enabled','S34 - Enabled'):
            # update list of channels in use
            self.getActiveMeasurements()
            # get selected parameter
            param = quant.name[:3]
            value = (param in self.dMeasParam)
        elif quant.name in ('S11', 'S21', 'S31','S41','S22','S12','S32','S42','S33','S13','S23','S43','S44','S14','S24','S34'):
            # check if channel is on
            if quant.name not in self.dMeasParam:
                # get active measurements again, in case they changed
                self.getActiveMeasurements()
            if quant.name in self.dMeasParam:
                if self.getModel() in ('E5071C',):
                    # new trace handling, use trace numbers
                    self.writeAndLog("CALC:PAR%d:SEL" % self.dMeasParam[quant.name])
                else:
                    # old parameter handing, select parameter (use last in list)
                    sName = self.dMeasParam[quant.name][-1]
                    self.writeAndLog("CALC:PAR:SEL '%s'" % sName)
                # if not in continous mode, trig from computer
                bWaitTrace = self.getValue('Wait for new trace')
                bAverage = self.getValue('Average')
                # wait for trace, either in averaging or normal mode
                if bWaitTrace:
                    if bAverage:
                        # set channels 1-4 to set event when average complete (bit 1 start)
                        self.writeAndLog(':SENS:AVER:CLE;:STAT:OPER:AVER1:ENAB 30;:ABOR;:SENS:AVER:CLE;')
                    else:
                        self.writeAndLog(':ABOR;:INIT:CONT OFF;:INIT:IMM;')
                        self.writeAndLog('*OPC')
                    # wait some time before first check
                    self.wait(0.03)
                    bDone = False
                    while (not bDone) and (not self.isStopped()):
                        # check if done
                        if bAverage:
                            sAverage = self.askAndLog('STAT:OPER:AVER1:COND?')
                            bDone = int(sAverage)>0
                        else:
                            stb = int(self.askAndLog('*ESR?'))
                            bDone = (stb & 1) > 0
                        if not bDone:
                            self.wait(0.03)
                    # if stopped, don't get data
                    if self.isStopped():
                        self.writeAndLog('*CLS;:INIT:CONT ON;')
                        return []
                # get data as float32, convert to numpy array
                if self.getModel() in ('E5071C',):
                    # new trace handling, use trace numbers
                    self.write(':FORM:DATA REAL32;:CALC:SEL:DATA:SDAT?', bCheckError=False)
                else:
                    # old parameter handing
                    self.write(':FORM REAL,32;CALC:DATA? SDATA', bCheckError=False)
                sData = self.read(ignore_termination=True)
                if bWaitTrace and not bAverage:
                    self.writeAndLog(':INIT:CONT ON;')
                # strip header to find # of points
                i0 = sData.find(b'#')
                nDig = int(sData[i0+1:i0+2])
                nByte = int(sData[i0+2:i0+2+nDig])
                nData = int(nByte/4)
                nPts = int(nData/2)
                # get data to numpy array
                vData = np.frombuffer(sData[(i0+2+nDig):(i0+2+nDig+nByte)],
                                      dtype='>f', count=nData)
                # data is in I0,Q0,I1,Q1,I2,Q2,.. format, convert to complex
                mC = vData.reshape((nPts,2))
                vComplex = mC[:,0] + 1j*mC[:,1]
                # get start/stop frequencies
                startFreq = self.readValueFromOther('Start frequency')
                stopFreq = self.readValueFromOther('Stop frequency')
                sweepType = self.readValueFromOther('Sweep type')
                # if log scale, take log of start/stop frequencies
                if sweepType == 'Log':
                    startFreq = np.log10(startFreq)
                    stopFreq = np.log10(stopFreq)
                # create a trace dict
                value = InstrumentQuantity.getTraceDict(vComplex, t0=startFreq,
                                               dt=(stopFreq-startFreq)/(nPts-1))
            else:
                # not enabled, return empty array
                value = InstrumentQuantity.getTraceDict([])
        elif quant.name in ('Wait for new trace',):
            # do nothing, return local value
            value = quant.getValue()
        else:
            # for all other cases, call VISA driver
            value = VISA_Driver.performGetValue(self, quant, options)
        return value


    def getActiveMeasurements(self):
        """Retrieve and a list of measurement/parameters currently active"""
        # proceed depending on model
        if self.getModel() in ('E5071C',):
            # in this case, meas param is just a trace number
            self.dMeasParam = {}
            # get number or traces
            nTrace = int(self.askAndLog(":CALC:PAR:COUN?"))
            # get active trace names, one by one
            for n in range(nTrace):
                sParam = self.askAndLog(":CALC:PAR%d:DEF?" % (n+1))
                self.dMeasParam[sParam] = (n+1)
        else:
            sAll = self.askAndLog("CALC:PAR:CAT:EXT?")
            # strip "-characters
            sAll = sAll[1:-1]
            # parse list, format is channel, parameter, ...
            self.dMeasParam = {}
            lAll = sAll.split(',')
            nMeas = len(lAll)//2
            for n in range(nMeas):
                sName = lAll[2*n]
                sParam = lAll[2*n + 1]
                if sParam not in self.dMeasParam:
                    # create list with current name
                    self.dMeasParam[sParam] = [sName,]
                else:
                    # add to existing list
                    self.dMeasParam[sParam].append(sName)



if __name__ == '__main__':
    pass
