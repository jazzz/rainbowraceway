import introspect
import admin_behaviours
import race_behaviours

import sys
current_module = sys.modules[__name__]

def generateClasses():
    p = introspect.getAssociatedObjects(admin_behaviours)
    for x in p:
        setattr(current_module,x.association,type(x.association, (object,), {}))

    p = introspect.getAssociatedObjects(race_behaviours)
    for x in p:
        setattr(current_module, x.association, type(x.association, (object,), {}))

def typeFromString(s):
    return getattr(current_module,s)

generateClasses()
