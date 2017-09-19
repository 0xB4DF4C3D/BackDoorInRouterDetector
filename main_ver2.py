import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import SSHutil
import random, time, datetime


# Start config -=-=-=-=-=-=-=-=-=-=-=-=-=

module = 'IF-MIB'
x1 = ['ifOutOctets','ifOutUcastPkts'][1]
x2 = ['ifInOctets','ifInUcastPkts'][1]
title = 'SNMP_{}&{}'.format(x1, x2)

delay = 10 # second (10~)

# End config -=-=-=-=-=-=-=-=-=-=-=-=-=-=

CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')

traceNames = [x1, x2, 'diff', 'variation','cmd']
TP = pg.TracePool(traceNames)

print("{} logging start..".format(title))


mySSH = SSHutil.SSH('10.0.0.2','admin','root')
mySSH.send('en')
mySSH.send('1234')

SSHcmds = ['Null','Null','Null','ping 40.0.0.101 size 15000 timeout 1 repeat 1','Null','Null','Null','ping 40.0.0.101 size 2000 timeout 1 repeat 9']
SSHcmdsLen = len(SSHcmds)
#SSHcmds = ['']

prevX = 0
cmdIdx = 0

try:
    while True:
        x1Res  = CG.getBulk('{}.{}'.format(module, x1), sq.accumulateEx([1,2,4]))
        x2Res = CG.getBulk('{}.{}'.format(module, x2), sq.accumulateEx([1,2,4]))
        
        mySSH.send(SSHcmds[cmdIdx%SSHcmdsLen])

        x = datetime.datetime.now().strftime('%H:%M:%S')
        ys = [x1Res, x2Res, x1Res-x2Res, ((x1Res-x2Res)-prevX)]

        for name, y in zip(TP, ys):
            if name in ['cmd']:
                continue
            TP.addData(name, {'x':[x],'y':[y]})
        TP.addData('cmd', {'x':[x],'y':[y], 'text':SSHcmds[cmdIdx%SSHcmdsLen]})
        

        print(datetime.datetime.now().strftime('%H:%M:%S'))
        print("{:<10} : {}".format(x1, x1Res))
        print("{:<10} : {}".format(x2, x2Res))
        print("{:<10} : {}".format("diff", x1Res-x2Res))
        print("{:<10} : {}".format('variation', ((x1Res-x2Res)-prevX)))
        print()

        prevX = x1Res-x2Res
        cmdIdx += 1
        time.sleep(delay)

finally:
    traces = [
    TP.getTrace(x1, {'line':dict(
        color = ('rgb(0,255,0)'),
        width = 4,
        dash = 'dash'
        )}),

    TP.getTrace(x2, {'line':dict(
        color = ('rgb(0,0,255)'),
        width = 4,
        dash = 'dash'
        )}),
    
    TP.getTrace('diff', {'line':dict(
        color = ('rgb(127,127,0)'),
        width = 2,
        dash = 'dot'
        )}),

    TP.getTrace('variation', {'line':dict(
        color = ('rgb(255,0,0)'),
        width = 2,
        dash = 'dashdot'
        )}),
    
    TP.getTrace('cmd', {'line':dict(
        color = ('rgb(0,0,0)'),
        width = 4
        ),'mode':'markers'})
    ]
    G = pg.Graph()
    figure = G.getFigure(traces, title)
    G.plot(figure, title)
    
