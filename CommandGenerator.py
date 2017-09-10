

from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

import SNMPqueries as sq
import time

class CommandGenerator():
    """
    General functions for SNMP command.

    """
    def __init__(self, name, key, agentIP, agentPort=161, SNMPversion=3):
        self.__cmdGen = cmdgen.CommandGenerator()
        if SNMPversion == 3:
            self.__userData = cmdgen.UsmUserData(name, key, key,
                           authProtocol=usmHMACSHAAuthProtocol,
                           privProtocol=usmDESPrivProtocol)
        else:
            raise NotImplementedError("SMMP version {} is not implemented.." % (SNMPversion))
        
        self.__target = cmdgen.UdpTransportTarget((agentIP, agentPort))


    # SNMP commands start with `Strategy pattern` -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    def walk(self, mibPath, func):
        return self.__funcMap(*self.__cmdGen.nextCmd(*self.__initCmdData(mibPath), lookupValues=True), func)

    def getBulk(self, mibPath, func):
        return self.__funcMap(*self.__cmdGen.bulkCmd(
            self.__userData,
            self.__target,
            0,50,
            cmdgen.MibVariable(*mibPath.split('.')),
           lookupValues=True), func)

    def get(self, mibPath, func):
        return self.__funcMap(*self.__cmdGen.getCmd(*self.__initCmdData(mibPath), lookupValues=True), func)
    # SNMP commands end -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


    # Internal function start -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    def __initCmdData(self, mibPath):
        """
        Initialize data with default information(userdata, target)
        and interpret a mib path.
        """
        return  (
            self.__userData,
            self.__target,
            cmdgen.MibVariable(*mibPath.split('.'))
        )


    def __funcMap(self, errorIndication, errorStatus, errorIndex, varBindTable, func):
        """
        Map given function for varBindTable
        plus, error handling.
        return value depends on func
        """
        if errorIndication:             # Error handling_1
            print(errorIndication)
        else:
            if errorStatus:             # Error handling_2
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                    )
                )
            else:
                return func(varBindTable)
