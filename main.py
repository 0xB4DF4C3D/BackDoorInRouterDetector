import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import paramiko, SSHutil
import random, time, datetime, threading

def initSSH(host, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)

    return ssh

# for multiple ssh connection
def annotationThread(host, username, password, cmdList, annotationList, x, isEnd):


    ssh = initSSH(host, username=username, password=password)
    print(host,'thread start...')
    
    annotationList = annotationList

    while True:
        for cmd, msg, delay in cmdList:
            if cmd != '':
                if msg != '':
                    annotationList.addAnnotation(x[0], 0, msg)
                    
                ssh.exec_command(cmd)
                print('\t',host,':',msg)
                #ssh.close()
                ssh = initSSH(host, username=username, password=password)
                
            for _ in range(delay):
                time.sleep(1)
                if isEnd[0]:
                    return


# Start graph config -=-=-=-=-=-=-=-=-=-=-=-=-=

module = 'IF-MIB'
x1 = ['ifOutOctets','ifOutUcastPkts'][1]
x2 = ['ifInOctets','ifInUcastPkts'][1]
title = 'SNMP_{}&{}'.format(x1, x2)

delay = 10 # second (10~)

traceNames = [x1, x2, 'diff', 'variation']
TP = pg.TracePool(traceNames)

isEnd = [False]
globalX = [0]
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

# Case 1 : small size & less packet 
# Case 2 : big size & less packet
# Case 3 : small size & many packet
# Case 4 : big size & many packet
aliceSSHcmds = [('','',180),
                ('ping 30.0.0.101 -s 512 -i 1','ⓐ',180),
                ('\x03','ⓩ',1),
                ('ping 30.0.0.101 -s 2048 -i 1','ⓑ',180),
                ('\x03','ⓩ',1),
                ('ping 30.0.0.101 -s 512 -i 0.5','ⓒ',180),
                ('\x03','ⓩ',1),
                ('ping 30.0.0.101 -s 2048 -i 0.5','ⓓ',180),
                ('\x03','ⓩ',1)
                ]#(cmd, mdg, delay)
aliceAnonnotationList = pg.AnnotationList(ay=20, clicktoshow=True)

aliceSSH = threading.Thread(target=annotationThread,
                   args=('20.0.0.101','gns3','gns3', aliceSSHcmds,aliceAnonnotationList,globalX, isEnd
                         ))
                   

# End SSH config -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')


print("{} logging start..".format(title))


try:
    prevX = 0
    cmdIdx = 0
    aliceSSH.start()

    routerAy = -10
    
    while True:

        routerMsg = routerSSHtxts[cmdIdx%routerSSHcmdsLen]
        routerCmd = routerSSHcmds[cmdIdx%routerSSHcmdsLen]
        
        x1Res  = CG.getBulk('{}.{}'.format(module, x1), sq.accumulateEx([1,2,4]))
        x2Res = CG.getBulk('{}.{}'.format(module, x2), sq.accumulateEx([1,2,4]))

        x = datetime.datetime.now().strftime('%H:%M:%S')
        globalX[0] = x
        ys = [x1Res, x2Res, x1Res-x2Res, ((x1Res-x2Res)-prevX)]

        for name, y in zip(TP, ys):
            TP.addData(name, {'x':[x],'y':[y]})

        if routerMsg != '':
            routerAnonnotationList.addAnnotation(x, 0, routerMsg,ay=routerAy-30)

            routerAy *= -1
            routerSSH.send(routerCmd)
            print(routerMsg)
        
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
    print('logging end..')
    isEnd[0] = True
    aliceSSH.join()
    print('thread end..')

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
    
