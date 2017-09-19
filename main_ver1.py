import CommandGenerator as cg
import SNMPqueries      as sq
import SSHutil
import random, time, datetime

# Start config -=-=-=-=-=-=-=-=-=-=-=-=-=

module = 'IF-MIB'
x1 = ['ifOutOctets','ifOutUcastPkts'][1]
x2 = ['ifInOctets','ifInUcastPkts'][1]
title = 'SNMP_{}&{}'.format(x1, x2)

plotlyOnline = True

delay = 10 # second (10~)

# End config -=-=-=-=-=-=-=-=-=-=-=-=-=-=

CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')

if plotlyOnline:
    import PlotlyGrapher as pg

    G = pg.Graph()

    traceNames = [x1, x2, 'diff', 'variation','cmd']

    SP = pg.StreamPool(traceNames)
    traces = []
    traces += [G.getTrace(name=x1, stream=SP.getStreamDict(x1, 256), line=dict(
        color = ('rgb(0,255,0)'),
        width = 4,
        dash = 'dash'
        ))]
    traces += [G.getTrace(name=x2, stream=SP.getStreamDict(x2, 256), line=dict(
        color = ('rgb(0,0,255)'),
        width = 4,
        dash = 'dash'
        ))]
    traces += [G.getTrace(name='diff', stream=SP.getStreamDict('diff', 256), line=dict(
        color = ('rgb(127,127,0)'),
        width = 2,
        dash = 'dot'
        ))]
    traces += [G.getTrace(name='variation', stream=SP.getStreamDict('variation', 256), line=dict(
        color = ('rgb(255,0,0)'),
        width = 2,
        dash = 'dashdot'
        ))]
    traces += [G.getTrace(name='cmd', stream=SP.getStreamDict('cmd', 256), mode='markers', line=dict(
        color = ('rgb(0,0,0)'),
        width = 4
        ))]

    figure = G.getFigure(traces, title)

    G.plot(figure, title)

    for traceName in SP:
        SP[traceName].open()
        SP.clearStream(traceName)

else:
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
        
        if plotlyOnline:
            x = datetime.datetime.now().strftime('%H:%M:%S')

            ys = [x1Res, x2Res, x1Res-x2Res, ((x1Res-x2Res)-prevX)]
            
            yIdx = 0
            for traceName in SP:
                if traceName in ['cmd']:
                    continue
                SP[traceName].write(dict(x=x,y=ys[yIdx]))
                yIdx += 1

            SP['cmd'].write(dict(x=x,y=0,text=SSHcmds[cmdIdx%SSHcmdsLen]))


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
    for traceName in SP:
        SP[traceName].close()
    print('all streaming closed')
