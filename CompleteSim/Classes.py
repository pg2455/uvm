class Action(object):

    def __init__(self, down, right, dead, rdown, rright, rdead, name):
        self.transition = {"down":down, "right": right, "dead": dead}
        self.reward = {"down":rdown, "right": rright, "dead": rdead}
        self.name = name


class Grid(object):

    def __init__(self, nrows, ncols, actions = []):
        self.actions = actions
        deadState = State(-1000, dead = True)
        self.states = {-1000 : deadState}
        self.ValueMatrix = {-1000: 0}

        for x in range(nrows*ncols):
            self.states[x] = State(x, dead = False, deadState = deadState, policy = {a:1.0/len(actions) for a in actions})
            self.ValueMatrix[x] = 0

        for i in range(ncols):
            for j in range(nrows):
                number = j + i * nrows

                if j != nrows - 1:
                    self.states[number].addDown(self.states[number+1])

                if i != ncols - 1:
                    self.states[number].addRight(self.states[number + nrows])



    def __str__(self):
        string = {}
        for i in self.states:
            string[i] = str(self.states[i])

        return str(string)



class State(object):

    def __init__(self, number, dead = False, deadState = None, policy = None):
        self.policy = policy
        self.id = number
        self.next = {}
        if not dead:
            self.next['dead'] = deadState

    def __str__(self):
        string = ""
        if 'down' in self.next:
            string += "|" + str(self.next['down'].id)

        if 'right' in self.next:
            string += "->" + str(self.next['right'].id)

        return string

    def addRight(self, state):
        self.next['right'] = state

    def addDown(self, state):
        self.next['down'] = state
