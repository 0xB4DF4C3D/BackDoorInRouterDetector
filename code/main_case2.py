import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import paramiko, SSHutil
import random, time, datetime, threading

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
    
