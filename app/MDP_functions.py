def getActionDict(ACTIONS):
    return {x:0.0 for x in ACTIONS}

def updateQ(prev_state, next_state, action, reaction):

    # update equation
    Q = learnedObjects.vars['Q'] # it makes a copy
    Q[prev_state][action] = Q[prev_state][action] + \
                setupVars.vars['ALPHA'] *( setupVars.vars['REACTION_REWARD'][action][reaction] + setupVars.vars['GAMMA']* max(Q[next_state].itervalues()) - Q[prev_state][action] )



def recordPolicy(prev_state, action):
    used_policy[prev_state][action]+=1



def updateVandPolicy():
    Q = learnedObjects.vars['Q'] # it makes a copy of the name and not create a new object
    V = learnedObjects.vars['V']
    policy = learnedObjects.vars['OPTIMAL_POLICY']

    for i in V:
        _max =  max(Q[i].iteritems(), key= lambda x:x[1])[1]
        V[i] = _max[1]
        policy[i] = _max[0]

def hoardPageValue():
    pass

#
# #test
# {u'feedback': [{u'action': u'nothing', u'reaction': u'down', u'prev_state': 1, u'next_state': 2}, {u'action': u'nothing', u'reaction': u'down', u'prev_state': 2, u'next_state': 3}, {u'action': u'nothing', u'reaction': u'down', u'prev_state': 3, u'next_state': 4}, {u'action': u'nothing', u'reaction': u'dead', u'prev_state': 4, u'next_state': 1000}]}
#
o='''
$.ajax({
      url: "http://0.0.0.0:9090/feedback",
      contentType: 'application/json; charset=UTF-8',
      data: JSON.stringify({feedback: [{action: 'nothing', reaction: 'down', prev_state: 1, next_state: 2}]}),
      type:"POST",
    });

'''

import random
from collections import defaultdict
class setup(object):
    def __init__(self):
        self.vars = {}

    def save(self):
        json.dump(self.vars,open('./static/parameters.json', 'w'))


setupVars = setup()
setupVars.vars['ACTIONS']  = ['nothing', 'video']
setupVars.vars['REACTION_REWARD'] = {action: {r:random.random() for r in ['down', 'right', 'dead']} for action in setupVars.vars['ACTIONS']}
setupVars.vars['MAX_ATSOP_ROWS'] = 10
setupVars.vars['MAX_SD_COLS'] = 6

setupVars.vars['GAMMA'] = 0.9
setupVars.vars['ALPHA'] = 0.5


def simulate():
    # P_ss'^a
    from collections import defaultdict
    ncells = [x for x in range(100)] + [999]
    transitionProbs = defaultdict(dict)
    for x in ncells:
        for action in setupVars.vars['ACTIONS']:
            down = random.random()
            dead = random.random()
            right = random.random()
            total = sum([down,dead, right])
            down,dead,right = down/total, dead/total, right/total

            transitionProbs[x+1][action] = {'down':down, 'dead':dead, 'right':right}

    Q = {x+1:{y:random.random() for y in setupVars.vars['ACTIONS']} for x in ncells}

def optimize(Q,P, epsilon):
    P = transitionProbs
    epsilon = 0.2
    current_policy = optimizePolicy(Q)

    # start with cell 1 --> generate the episode
    for i in range(10):
        #episode
        s0 = 1
        action0 = decideAction(current_policy[s0], setupVars.vars['ACTIONS'], epsilon)
        while s0 != 1000:
            reaction = weighted_choice(list(P[s0][action0].iteritems()))
            reward = setupVars.vars['REACTION_REWARD'][action][reaction]
            s1 = getNewCell(s0, reaction)
            action1 = decideAction(current_policy[s1], setupVars.vars['ACTIONS'], epsilon)

            Q[s0][action] = Q[s0][action] + setupVars.vars['ALPHA'] * (reward + setupVars.vars['GAMMA']* Q[s1][action1] - Q[s0][action])
            # print(s0, " --> ", s1)
            s0 = s1
            action0 = action1
        # print "_______________________"

    # several episodes


def getNewCell(s,reaction):
    if reaction == 'dead':
        return 1000

    if s % setupVars.vars['MAX_ATSOP_ROWS'] == 0 :
        if reaction == 'down':
            return s
    if 1 + s/setupVars.vars['MAX_ATSOP_ROWS'] > setupVars.vars['MAX_SD_COLS']:
        if reaction == 'right':
            return s

    if reaction == 'right':
        return s + setupVars.vars['MAX_ATSOP_ROWS']

    if reaction == 'down':
        return s + 1
