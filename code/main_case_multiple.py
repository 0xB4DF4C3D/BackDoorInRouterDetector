import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import paramiko, SSHutil
import random, time, datetime, threading

SPOOF = False

routerList = ['10.0.0.4', '10.0.0.5', '10.0.0.6',
              '10.0.0.7', '10.0.0.8', '10.0.0.9']

agentList = {f"R{ip.split('.')[-1]}":
            cg.CommandGenerator('dongho','yen030519','kw971220',ip)
            for ip in routerList}

#linkStatus = [('R4.3', 'R5.3'), ('R4.1', 'R6.3'), ('R4.4', 'R7.1'), ('R5.2', 'R7.5'),
#            ('R6.4', 'R8.1'), ('R7.2', 'R8.4'), ('R7.6', 'R9.2'), ('R8.3', 'R9.3')]

linkStatus = [('R4.1', 'R6.3')]

delay = 10 # second (10~)

inUStatus = {}
inNUStatus = {}
inSumStatus = {}
prevInStatus = {}

outUStatus = {}
outNUStatus = {}
outSumStatus = {}

while True:
    offset = {}

    for agent in agentList:
        inUStatus[agent] = agentList[agent].getBulk('IF-MIB.ifInUcastPkts', sq.byDict)
        inNUStatus[agent] = agentList[agent].getBulk('IF-MIB.ifInNUcastPkts', sq.byDict)
        outUStatus[agent] = agentList[agent].getBulk('IF-MIB.ifOutUcastPkts', sq.byDict)
        outNUStatus[agent] = agentList[agent].getBulk('IF-MIB.ifOutNUcastPkts', sq.byDict)

    inStatus = {i:{j:inUStatus[i][j]+inNUStatus[i][j] for j in inUStatus[i]} for i in inUStatus}
    outStatus = {i:{j:outUStatus[i][j]+outNUStatus[i][j] for j in outUStatus[i]} for i in outUStatus}

    for inName, outName in zip(inStatus, outStatus):
        inSum = 0
        outSum = 0
        for inVal, outVal in zip(inStatus[inName], outStatus[outName]):
            inSum += inStatus[inName][inVal]
            outSum += outStatus[outName][outVal]
        inSumStatus[inName] = inSum
        outSumStatus[outName] = outSum

    if len(prevInStatus) == 0:
        prevInSumStatus = inSumStatus.copy()
        prevOutSumStatus = outSumStatus.copy()

    for a, b in linkStatus:
        aName, aInt = a.split('.')
        bName, bInt = b.split('.')

        if SPOOF:
            ioVar = (inSumStatus[aName] - outSumStatus[aName]) - (prevInSumStatus[aName] - prevOutSumStatus[aName])
            if abs(ioVar) > 100:
                print(f"ioVar over the threshold! [{ioVar}]")
                offset[aName] = -ioVar
                inSumStatus[aName] += offset[aName]
                if random.random() > .5:
                    inStatus[aName][aInt] -= offset[aName]
                else:
                    outStatus[aName][aInt] -= offset[aName]
        
        aIn, aOut = inStatus[aName][aInt], outStatus[aName][aInt]
        bIn, bOut = inStatus[bName][bInt], outStatus[bName][bInt]

        if len(prevInStatus) > 0:
            paIn, paOut = prevInStatus[aName][aInt], prevOutStatus[aName][aInt]
            pbIn, pbOut = prevInStatus[bName][bInt], prevOutStatus[bName][bInt]
        else:
            paIn, paOut, pbIn, pbOut = aIn, aOut, bIn, bOut
        
        #print(aName, aInt, bName, bInt)
        #print(f"{aName}:{inStatus[aName][aInt]},{outStatus[aName][aInt]}\n{bName}:{outStatus[bName][bInt]},{inStatus[bName][bInt]}\n\n")
        print(f"<{aName}.{aInt}, {bName}.{bInt}>")
        print(f"{aName} in {aIn} <-> {bName} out {bOut} .. var {(aIn - bOut) - (paIn - pbOut)}")
        print(f"{aName} out {aOut} <-> {bName} in {bIn} .. var {(aOut - bIn) - (paOut - pbIn)}")
        print()
        
    for agent in agentList:
        print(f"{agent} IO var : {(inSumStatus[agent] - outSumStatus[agent]) - (prevInSumStatus[agent] - prevOutSumStatus[agent])}")
        
    prevInSumStatus = inSumStatus.copy()
    prevOutSumStatus = outSumStatus.copy()
    prevInStatus = inStatus.copy()
    prevOutStatus = outStatus.copy()

    for agent in offset:
        prevInSumStatus[agent] -= offset[agent]
    
    print("\n\n")
    time.sleep(delay)



'''
 for a, b in linkStatus:
	aName, aVal = a.split('.')
	bName, bVal = b.split('.')
	
R4.1 f1/0
R4.2 f2/0
R4.3 f0/0
R4.4 f0/1

R5.1 f1/0
R5.2 f0/0
R5.3 f0/1

R6.1 f1/0
R6.2 f2/0
R6.3 f0/0
R6.4 f0/1

R7.1 f1/0
R7.2 f2/0
R7.3 f3/0
R7.4 f4/0
R7.5 f0/0
R7.6 f0/1

R8.1 f1/0
R8.2 f2/0
R8.3 f0/0
R8.4 f0/1

R9.1 f1/0
R9.2 f0/0
R9.3 f0/1

(R4.3, R5.3), (R4.1, R6.3), (R4.4, R6.1), (R5.2, R7.5),
(R6.4, R8.1), (R7.2, R8.4), (R7.6, R9.2), (R8.3, R9.3)

[('R4.3', 'R5.3'), ('R4.1', 'R6.3'), ('R4.4', 'R6.1'), ('R5.2', 'R7.5'),
('R6.4', 'R8.1'), ('R7.2', 'R8.4'), ('R7.6', 'R9.2'), ('R8.3', 'R9.3')]
'''

'''
# Start graph config -=-=-=-=-=-=-=-=-=-=-=-=-=

module = 'IF-MIB'
xOut = ['ifOutOctets','ifOutUcastPkts']
xIn = ['ifInOctets','ifInUcastPkts']
title = 'SNMP_{}&{}'.format('Octet variation', 'Pkt variation')

delay = 10 # second (10~)

traceNames = ['Octet variation', 'Pkt variation']
TP = pg.TracePool(traceNames)
# End graph config -=-=-=-=-=-=-=-=-=-=-=-=-=-=



# Start SSH config -=-=-=-=-=-=-=-=-=-=-=-=-=-=

gap = lambda x : ['']*x

routerSSH = SSHutil.SSH('10.0.0.2','admin','root')
routerSSH.send('en')
routerSSH.send('1234')

routerSSHcmds = [*gap(6),'ping 40.0.0.101 size 15000 timeout 1 repeat 1',
                 *gap(6),'ping 40.0.0.101 size 2000 timeout 1 repeat 9']
routerSSHtxts = [*gap(6),'①',
                 *gap(6),'②']
routerSSHcmdsLen = len(routerSSHcmds)
routerAnonnotationList = pg.AnnotationList(ax=-60, ay=-60, clicktoshow=True)

# End SSH config -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')


print("{} logging start..".format(title))


try:
    prevX1 = 0
    prevX2 = 0
    cmdIdx = 0

    routerAy = -10
    
    while True:

        routerMsg = routerSSHtxts[cmdIdx%routerSSHcmdsLen]
        routerCmd = routerSSHcmds[cmdIdx%routerSSHcmdsLen]
        
        xInputRes1  = CG.getBulk('{}.{}'.format(module, xIn[0]), sq.accumulateEx([1,2,4]))
        xOutputRes1 = CG.getBulk('{}.{}'.format(module, xOut[0]), sq.accumulateEx([1,2,4]))

        xInputRes2  = CG.getBulk('{}.{}'.format(module, xIn[1]), sq.accumulateEx([1,2,4]))
        xOutputRes2 = CG.getBulk('{}.{}'.format(module, xOut[1]), sq.accumulateEx([1,2,4]))

        x = datetime.datetime.now().strftime('%H:%M:%S')
        globalX[0] = x
        ys = [((xOutputRes1-xInputRes1)-prevX1), ((xOutputRes2-xInputRes2)-prevX2) * 1000]

        for name, y in zip(TP, ys):
            TP.addData(name, {'x':[x],'y':[y]})

        if routerMsg != '':
            routerAnonnotationList.addAnnotation(x, 0, routerMsg,ay=routerAy-30)

            routerAy *= -1
            routerSSH.send(routerCmd)
            print(routerMsg)
        
        print(datetime.datetime.now().strftime('%H:%M:%S'))
        print("{:<10} : {}".format('Octet var', ((xOutputRes1-xInputRes1)-prevX1)))
        print("{:<10} : {}".format('Pkt   var', ((xOutputRes2-xInputRes2)-prevX2)))
        print()

        prevX1 = xOutputRes1-xInputRes1
        prevX2 = xOutputRes2-xInputRes2
        cmdIdx += 1
        time.sleep(delay)
except Exception as e:
    print(e)
finally:
    print('logging end..')
    print('thread end..')

    annotations = routerAnonnotationList.getAnnotationList()
    
    TP.delDataElement('Octet variation','x',0)
    TP.delDataElement('Pkt variation','y',0)
    
    traces = [
    TP.getTrace('Octet variation', {'line':dict(
        color = ('rgb(0,255,0)'),
        width = 2,
        )}),

    TP.getTrace('Pkt variation', {'line':dict(
        color = ('rgb(0,0,255)'),
        width = 2,
        )})
    ]
    
    G = pg.Graph()
    figure = G.getFigure(traces, title, annotations=annotations)
    G.plot(figure, title)
    '''
