import sys

class _SNMPqueries():
    def __init__(self):
        # simple lambdas start -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        self.accumulate  = lambda tab : sum([int(i[0][1]) for i in tab])
        self.getSingle   = lambda var : var[0]
        # simple lambdas end -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        
    def printAll(self, tab):
        for row in tab:
            for name, val in row[:2]:
                print('%s : %s' % (name.prettyPrint(), val.prettyPrint()))

    def accumulateEx(self, instances):
        
        def InAccumulateEx(tab):
            sum = 0
            for row in tab:
                for name, val in row[:2]:
                    if(int(str(name).split('.')[-1]) in instances):
                        sum += int(val)
            return sum
        
        return InAccumulateEx

# To direct module access.
sys.modules[__name__] = _SNMPqueries()
