import sys

class _SNMPqueries():
    def __init__(self):
        # simple lambdas start -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        self.accumulateQuery = lambda tab : sum([i[0][1] for i in tab])
        self.getSingle       = lambda var : var[0]
        # simple lambdas end -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        
    def printAll(self, tab):
        for row in tab:
            for name, val in row:
                print('%s : %s' % (name.prettyPrint(), val.prettyPrint()))

# To direct module access.
sys.modules[__name__] = _SNMPqueries()
