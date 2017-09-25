import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import SSHutil
import random, time, datetime



# Start graph config -=-=-=-=-=-=-=-=-=-=-=-=-=

module = 'IF-MIB'
x1 = ['ifOutOctets','ifOutUcastPkts'][1]
x2 = ['ifInOctets','ifInUcastPkts'][1]
title = 'SNMP_{}&{}'.format(x1, x2)

delay = 10 # second (10~)

traceNames = [x1, x2, 'diff', 'variation']
TP = pg.TracePool(traceNames)

routerAnonnotationList = pg.AnnotationList(ax=-40, ay=-40)
aliceAnonnotationList = pg.AnnotationList(ax=-40, ay=40)

# End graph config -=-=-=-=-=-=-=-=-=-=-=-=-=-=



# Start SSH config -=-=-=-=-=-=-=-=-=-=-=-=-=-=

gap = lambda x : ['']*x

routerSSH = SSHutil.SSH('10.0.0.2','admin','root')
routerSSH.send('en')
routerSSH.send('1234')

routerSSHcmds = [*gap(6),'ping 40.0.0.101 size 15000 timeout 1 repeat 1',
                 *gap(6),'ping 40.0.0.101 size 2000 timeout 1 repeat 9']
routerSSHtxts = [*gap(6),'size 15000 & repeat 1',
                 *gap(6),'size 2000 & repeat 9']
routerSSHcmdsLen = len(routerSSHcmds)


aliceSSH = SSHutil.SSH('20.0.0.101','gns3','gns3')
aliceSSH.send('')
time.sleep(3)
aliceSSH.send('S')

# Case 1 : small size & less packet 
# Case 2 : big size & less packet
# Case 3 : small size & many packet
# Case 4 : big size & many packet
aliceSSHcmds = [*gap(18),
                'ping 30.0.0.101 -s 4096 -i 1', *gap(18), '\x03',
                'ping 30.0.0.101 -s 65536 -i 1', *gap(18), '\x03',
                'ping 30.0.0.101 -s 4096 -i 0.5', *gap(18), '\x03',
                'ping 30.0.0.101 -s 65536 -i 0.5', *gap(18), '\x03'
                ]
aliceSSHtxts = [*gap(18),
                'size 4096 & interval 1', *gap(18), 'stop',
                'size 65536 & interval 1', *gap(18), 'stop',
                'size 4096 & interval 0.5', *gap(18), 'stop',
                'size 65536 & interval 0.5', *gap(18), 'stop'
                ]
aliceSSHcmdsLen = len(aliceSSHcmds)


# End SSH config -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')


print("{} logging start..".format(title))


try:
    prevX = 0
    cmdIdx = 0
    routerAy = -10
    while True:
        
        routerMsg = routerSSHtxts[cmdIdx%routerSSHcmdsLen]
        aliceMsg = aliceSSHtxts[cmdIdx%aliceSSHcmdsLen]
        routerCmd = routerSSHcmds[cmdIdx%routerSSHcmdsLen]
        aliceCmd = aliceSSHcmds[cmdIdx%aliceSSHcmdsLen]
        
        
        x1Res  = CG.getBulk('{}.{}'.format(module, x1), sq.accumulateEx([1,2,4]))
        x2Res = CG.getBulk('{}.{}'.format(module, x2), sq.accumulateEx([1,2,4]))
        
        x = datetime.datetime.now().strftime('%H:%M:%S')
        ys = [x1Res, x2Res, x1Res-x2Res, ((x1Res-x2Res)-prevX)]

        for name, y in zip(TP, ys):
            TP.addData(name, {'x':[x],'y':[y]})

        if routerMsg != '':
            routerAnonnotationList.addAnnotation(x, y, routerMsg,ay=routerAy-30)
            routerAy *= -1
            routerSSH.send(routerCmd)
            print(routerMsg)

        if aliceMsg != '':
            aliceAnonnotationList.addAnnotation(x, y, aliceMsg)
            aliceSSH.send(aliceCmd)
            print(aliceMsg)
        
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
    annotations = routerAnonnotationList.getAnnotationList() + aliceAnonnotationList.getAnnotationList()
    
    TP.delDataElement('variation','x',0)
    TP.delDataElement('variation','y',0)
    
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
        )})
    ]
    
    G = pg.Graph()
    figure = G.getFigure(traces, title, annotations=annotations)
    G.plot(figure, title)
    
