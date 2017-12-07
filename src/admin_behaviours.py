from introspect import Associate

@Associate("blue")
def test1(ctrl,ctx):
    print("test1")

def test2(ctrl,ctx):
    print("test2")

@Associate("red")
def test3(ctrl,ctx):
    print("test2")

