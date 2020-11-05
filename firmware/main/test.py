importCount = 0
somevar = 0


class Test:
    def __init__(self):
        global importCount
        print("test class just initialized, time number {}".format(importCount))
        importCount += 1


def do_something():
    print("here we go")


def modify():
    global somevar
    somevar += 1


def output():
    global somevar
    return somevar
