import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import paramiko, SSHutil
import random, time, datetime
import msvcrt, os, sys

def initSSH(host, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)

    return ssh

SPOOF = False
dataSize = 100

routerList = ['10.0.0.4', '10.0.0.5', '10.0.0.6',
              '10.0.0.7', '10.0.0.8', '10.0.0.9']

agentList = {f"R{ip.split('.')[-1]}":
            cg.CommandGenerator('dongho','yen030519','kw971220',ip)
            for ip in routerList}

linkStatus = [('R4.3', 'R5.3'), ('R4.1', 'R6.3'), ('R4.4', 'R7.1'), ('R5.2', 'R7.5'),
            ('R6.4', 'R8.1'), ('R7.2', 'R8.4'), ('R7.6', 'R9.2'), ('R8.3', 'R9.3')]

delay = 10 # second (10~)
G = pg.Graph()
SP = pg.StreamPool(list(agentList.keys()))
TP = pg.TracePool(list(agentList.keys()))
traces = [TP.getTrace(name=i, info=dict(stream=SP.getStreamDict(i, 256))) for i in SP]
figure = G.getFigure(traces, 'SNMP-Monitoring')
G.plot(figure, 'SNMP-Monitoring')

for S in SP:
    SP[S].open()
    SP.clearStream(S)

inUStatus = {}
inNUStatus = {}
inSumStatus = {}
prevInStatus = {}

outUStatus = {}
outNUStatus = {}
outSumStatus = {}

try:
    while True:
        offset = {}
        normal = True
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
        
        os.system('cls')
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
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
                
            isOverThreshold = "Abnormal" if abs((aIn - bOut) - (paIn - pbOut)) > 100 or ((aOut - bIn) - (paOut - pbIn)) > 100 else "Normal" 
            if isOverThreshold != 'Normal': normal = False
            
            print(f"<{aName}.{aInt}, {bName}.{bInt}> {isOverThreshold}")
            print(f"{aName} in {aIn} <-> {bName} out {bOut} .. var {(aIn - bOut) - (paIn - pbOut)}")
            print(f"{aName} out {aOut} <-> {bName} in {bIn} .. var {(aOut - bIn) - (paOut - pbIn)}")
            print()
        cur = datetime.datetime.now().strftime('%H:%M:%S')
        for agent in agentList:
            ioVar = (inSumStatus[agent] - outSumStatus[agent]) - (prevInSumStatus[agent] - prevOutSumStatus[agent])
            SP[agent].write(dict(x=cur,y=ioVar))
            if abs(ioVar) > 100: normal = False
            print(f"{agent} IO var : {ioVar}")
        if not normal:
            print("[!] Warning! Malicious pattern detected!")
        print()
        
        prevInSumStatus = inSumStatus.copy()
        prevOutSumStatus = outSumStatus.copy()
        prevInStatus = inStatus.copy()
        prevOutStatus = outStatus.copy()

        for agent in offset:
            prevInSumStatus[agent] -= offset[agent]
        
        for i in range(delay*10):
            time.sleep(0.1)
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch == b's':
                    print("[!] SPOOF ON")
                    SPOOF = True
                elif ch == b'S':
                    print("[!] SPOOF OFF")
                    SPOOF = False
                elif ch >= b'4' and ch <= b'7':
                    print(f"[!] Eavesdrop by R{ch.decode('ascii')}.. ", end=' ')
                    sys.stdout.flush()
                    ssh = initSSH(f"10.0.0.{ch.decode('ascii')}",'root','root')
                    shell = ssh.invoke_shell()
                    time.sleep(3)
                    shell.send("en\n"); shell.recv(9999); time.sleep(0.5);
                    shell.send("root\n"); shell.recv(9999); time.sleep(0.5);
                    shell.send(f"ping 101.0.0.2 repeat {dataSize} timeout 0\n"); time.sleep(0.008*dataSize)
                    shell.close()
                    print("done!")
                elif ch == b'q':
                    print(f"dataSize {dataSize} -> {dataSize+100}")
                    dataSize += 100
                elif ch == b'a':
                    print(f"dataSize {dataSize} -> {dataSize-100}")
                    dataSize -= 100

            
except Exception as e:
    print(e)
    
finally:
    for S in SP:
        SP.freeStream(SP[S])
    print("done")
