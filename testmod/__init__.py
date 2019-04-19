from .a import a
from .submod.d import d

def c(a, b):
    return a + b

class b():
    def __init__(self):
        print("b")
        a()
        d()