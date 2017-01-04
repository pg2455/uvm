class Stack(object):
    def __init__(self, alist):
        self.list = alist
        self.index = len(alist)

    def push(self, x):
        self.list.append(x)
        self.index += 1

    def pop(self):
        self.index -= 1
        return self.list.pop(self.index)


# infix = "( ( A + B ) * C )"
def getPostFix(infix):
    token = infix.split()
    output = Stack([])
    temp = Stack([])

    for t in token:
        if t in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' or t in '0123456789':
            temp.push(t)
        elif t == '(':
            temp.push(t)
        elif t == ')':
            while True:
                x = temp.pop()
                if x == '(':
                    break
                output.push(x)
        else:
            output.push(t)
    print temp.list, output.list

    string = ''
    out = []
    while True:
        try:
            t = output.pop()
            if t not in '*+-/':
                string += t
            else:
                string+=t
                out.append(string)
                string =''
        except:
            break
        
    return "".join(out[::-1])


infix = "( ( A + B ) * ( C + D ) )"
