def getActionDict(ACTIONS):
    return {x:0.0 for x in ACTIONS}


def updateQ(Q,REACTION_REWARD,prev_state, next_state, action, reaction,ALPHA, GAMMA):

    # update equation
    Q[prev_state][action] = Q[prev_state][action] + \
                ALPHA *( REACTION_REWARD[action][reaction] + GAMMA* max(Q[next_state].itervalues()) - Q[prev_state][action] )

    return Q
def recordPolicy(prev_state, action):
    used_policy[prev_state][action]+=1


def optimizePolicy():
    pass


def writeToParametersJS(parameters):
    filename = './static/parameters.js'
    para_file = open(filename, 'w')
    for key in parameters:
        print key
        para_file.write(key + "=" + parameters[key])

    para_file.close()
