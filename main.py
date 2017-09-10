import CommandGenerator as cg
import SNMPqueries      as sq
import PlotlyGrapher    as pg
import random, time, datetime
'''
CG = cg.CommandGenerator('admin','1234','10.0.0.2')
G = pg.Graph()

traceNames = ['ipInReceives','ipOutRequests','ipInReceives - ipOutRequests']
SP = pg.StreamPool(traceNames)

traces = [G.getTrace(name=i, stream=SP.getStreamDict(i, 256)) for i in SP]
figure = G.getFigure(traces, 'SNMP-ipInReceives_ipOutRequests')

G.plot(figure, 'SNMP-ipInReceives_ipOutRequests')

for traceName in SP:
    SP[traceName].open()
    SP.clearStream(traceName)

while True:
    inPkts  = int(CG.walk('RFC1213-MIB.ipInReceives', sq.accumulate))
    outPkts = int(CG.walk('RFC1213-MIB.ipOutRequests', sq.accumulate))

    #CG.walk('IF-MIB.ifInOctets', sq.printAll)
    #CG.walk('IF-MIB.ifOutOctets', sq.printAll)
    #print('IN   : ', inPkts)
    #print('OUT  : ', outPkts)
    #print('DIFF : ', inPkts - outPkts)

    x = datetime.datetime.now().strftime('%H:%M:%S.%f')
    ys = [inPkts, outPkts, inPkts-outPkts]

    yIdx = 0
    for traceName in SP:
        SP[traceName].write(dict(x=x,y=ys[yIdx]))
        yIdx += 1
    
    time.sleep(2)
    '''


CG = cg.CommandGenerator('admin','kw123456','10.0.0.2')
CG.getBulk('IF-MIB.ifDescr', sq.printAll)
CG.getBulk('IF-MIB.ifSpeed', sq.printAll)
CG.getBulk('IF-MIB.ifSpeed', sq.accumulateEx([1,2,3]))
