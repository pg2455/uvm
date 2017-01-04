# user behavior
# probability of going down and right in each cell
import requests, random
# defined will be probability of reactions to actions as well
class Action(object):

    def __init__(self, down, right, dead, name):
        self.transition = {"down":down, "right": right, "dead": dead}
        self.name = name

class simulate(object):

    def __init__(self, nrows, ncols, wall_factor):
        self.nrows, self.ncols = nrows, ncols

        nothing = Action(down = 0.3, right = 0.3, dead = 0.3, name = 'nothing')
        video = Action(down = 0.5, right = 0, dead = 0.5, name = 'video')
        paywall1 = Action(down = 0.2, right = 0, dead = 0.8, name = 'paywall')
        paywall2 = Action(down = 0.4, right = 0, dead = 0.6, name = 'paywall')

        case1 = { x+1 : {nothing: 0.5, video: 0.5} for x in range(nrows*ncols) }
        case2 = { x+1 : {nothing: 0.9, paywall1: 0.1} if x+1 <= nrows * wall_factor else {nothing: 0.3, paywall2: 0.7} for x in range(nrows*ncols) }
        self.action_probs = case1
        self.actions = self.action_probs[1]
        self.source_probs = {'search': 0.3, 'social':0.3,  'direct': 0.3}

        self.action_map = { action.name[0]: action for action in self.actions}
        for action in self.action_probs[1]:
            self.action_map[action.name] = action


    def simulate(self, iterations):
        submitResponses(iterations, self.action_probs, self.nrows, self.ncols)
        self.getCPMStats('direct')

    def setOptimalPolicy(self):
        source = 'direct'
        self.action_probs = getOptimalPolicyFromApp(source,self.action_map)

    def getCPMStats(self, source):
        resp = requests.get('http://0.0.0.0:9090/getactionStats', json = {'source':source}).json()
        self.cpmstats = resp


def getActionStats(source):
    source = 'direct'
    resp = requests.get('http://0.0.0.0:9090/getactionStats', json = {'source':source}).json()
    return resp


def submitResponses(iterations, action_probs, nrows, ncols):
    for x in range(iterations):
        selectAndSetSource(source_probs)
        data = simulateUser(nrows, ncols, action_probs)
        sendFeedback(data)

def getOptimalPolicyFromApp(source,action_map):
    resp = requests.get('http://0.0.0.0:9090/getOptimalPolicyForSimulation', json = {'source':source}).json()
    return convertOptimalPolicyForSimulation(resp, action_map)

def convertOptimalPolicyForSimulation(policy, action_map):
    policy_ = map(lambda (cell,p):(int(cell),{action_map[p]:1.0}), policy.iteritems())
    return dict(policy_)

def selectAndSetSource(source_probs):
    source = 'direct' #selectRandom(list(source_probs.iteritems()))
    requests.post('http://0.0.0.0:9090/initiateSession', json = {'source': source})

def simulateUser(nrows, ncols, action_probs):
    start,sd = 1,1
    rightwall, bottomwall = False, False
    data = []
    while start != 1000:
        action =  takeAction(list(action_probs[start].iteritems()))
        reaction = react(action)
        if reaction == 'right' and rightwall == True:
            continue
        if reaction == 'down' and bottomwall == True:
            continue

        new_state,sd, rightwall, bottomwall = computeNextState(start, reaction, sd,nrows, ncols, rightwall, bottomwall)
        data.append({'reaction': reaction, 'url':"n/a", 'prev_state': start, 'next_state': new_state, 'SD': sd, 'action': action.name})
        start = new_state
        if action.name == 'paywall':
            break
    return data



def sendFeedback(data):
    # data= [{u'reaction': u'down', u'url': u'http://0.0.0.0:9090/loadHome', u'prev_state': 1, u'action': u'nothing', u'SD': 1, u'next_state': 2}, {u'reaction': u'dead', u'url': u'http://0.0.0.0:9090/loadHome', u'prev_state': 2, u'action': u'video', u'SD': 1, u'next_state': 1000}]
    requests.post('http://0.0.0.0:9090/feedback', json = {'feedback1': data})

def takeAction(action_probs):
    return selectRandom(action_probs)

def react(action):
    return selectRandom(list(action.transition.iteritems()))

def computeNextState(start, reaction, sd, nrows, ncols, rightwall, bottomwall):
    if reaction == 'dead':
        return (1000,sd, 1, 2)

    if reaction == 'right':
        if sd < ncols:
            sd += 1
            state = start + nrows

            if bottomwall == True:
                bottomwall = False

        elif sd == ncols:
            state = start
            rightwall = True

    if reaction == 'down':
        if start % nrows == 0:
            state = start
            bottomwall = True
        else:
            state = start + 1
            if rightwall == True:
                rightwall = False


    return (state, sd, rightwall, bottomwall)

def selectRandom(probs):
    if len(probs) == 1:
        return probs[0][0]
    # action probs - list of tuples; (object, prob)
    total_prob = sum(item[1] for item in probs)
    chosen = random.uniform(0, total_prob)
    cumulative = 0
    for action,probability in probs:
        cumulative += probability
        if cumulative > chosen:
            return action
