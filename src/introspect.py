import inspect
from collections import namedtuple

ObjAssociation = namedtuple("ObjAssociation",("name","obj","association"))

class AssociatedObjConflictException(Exception):
    pass

class Associate(object):
    @staticmethod
    def getExportField():
        return "_ASSOCIATED_OBJ_##"

    def __init__(self, association):
        self.association = association.lower().replace(' ','_')

    def __call__(self, f):
        def inner():
            setattr(f,self.getExportField(),self.association)
            return f
        return inner()

def getAssociatedObjects(module):
    all_functions = [x for x in inspect.getmembers(module, inspect.isfunction)]
    all_classes = [x for x in inspect.getmembers(module, inspect.isclass)]
    l = []

    for name, obj in all_functions + all_classes:
        if hasattr(obj, Associate.getExportField()):
            l.append(ObjAssociation(name,obj,getattr(obj,Associate.getExportField())))
    return l


def verifyObjAssociationSanity(module):
    try:
        l = getAssociatedObjects(module)
        assoc_list = list(map(lambda x: x.association,l))
        s = set([])
        for obj in assoc_list:
            if obj in s:
                raise AssociatedObjConflictException("Dublicate entries for %s"%(obj))
            s.add(obj)
    # Re-Raising to clean up the stack trace alittle
    except AssociatedObjConflictException as e:
        raise AssociatedObjConflictException(*e.args)


if __name__ == "__main__":
    import admin_behaviours
    import race_behaviours
    verifyObjAssociationSanity((admin_behaviours))
    p = getAssociatedObjects(admin_behaviours)
    print(p)