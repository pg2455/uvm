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
