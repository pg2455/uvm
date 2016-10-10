from flask import Response, Flask, request, jsonify, render_template, make_response, url_for,redirect, send_from_directory
import json, copy
# from flask.ext.socketio import SocketIO, emit
from collections import defaultdict
from flask_sockets import Sockets

class setup(object):
    def __init__(self):
        self.vars = {}

    def save(self):
        tmp = open('./static/parameters.json', 'w')
        json.dump(self.vars, tmp)
        tmp.close()

class userSourceData(object):
    def __init__(self):
        self.source ={'search':0, 'social':0, 'direct':0}
        self.currentSource = 'direct'

    def recordSource(self, source):
        self.source[source]+=1

    def getSimilarity(self, segment):
        if sum(self.source.values()) ==0:
            return 0
        return 1.0*self.source[segment]/sum(self.source.values())

class segmentData(object):
    def __init__(self):
        self.vars = {}

class learnedObjectsVars(object):
    def __init__(self):
        self.init()

    def init(self):
        self.vars = {}
        self.vars['OPTIMAL_Q'] = {}
        self.vars['OPTIMAL_V'] = {}
        self.observation = {}

    def save(self):
        json.dump(self.vars,open('./static/learnedObjects.json', 'w'))

    def updateQ(self, prev_state, next_state, action, reaction):
        # update equation
        Q = self.vars['Q'] # it makes a copy
        Q[prev_state][action] = Q[prev_state][action] + \
                    setupVars.vars['ALPHA'] *( setupVars.vars['REACTION_REWARD'][action][reaction] + setupVars.vars['GAMMA']* max(Q[next_state].itervalues()) - Q[prev_state][action] )

    def updateV(self, prev_state, next_state, action, reaction):
        V = self.vars['V']
        V[prev_state] = V[prev_state] +setupVars.vars['ALPHA']*(setupVars.vars['REACTION_REWARD'][action][reaction] + setupVars.vars['GAMMA']*V[next_state] - V[prev_state])

    def recordPolicy(self, prev_state, action):
        self.vars['EXECUTED_POLICY'][prev_state][action]+=1

    def updateVandPolicy(self):
        self.vars['OPTIMAL_POLICY'], _ = optimizePolicy(self.vars['Q'])

    def recordPageValue(self, url, reaction, action, sd):
        if url not in self.vars['pages']:
            self.vars['pages'][url][sd] = {a: {'sum':0, 'obs':0} for a in setupVars.vars['ACTIONS']}

        if sd not in self.vars['pages'][url]:
            self.vars['pages'][url][sd] = {a: {'sum':0, 'obs':0} for a in setupVars.vars['ACTIONS']}

        self.vars['pages'][url][sd][action]['sum'] +=  setupVars.vars['REACTION_REWARD'][action][reaction]
        self.vars['pages'][url][sd][action]['obs'] += 1

    def recordTransitionProbs(self, prev_state, action, reaction):
        self.observation[prev_state] = True
        # print self.observation.keys()
        self.vars['transitionProbs'][prev_state][action]['obs']+=1
        self.vars['transitionProbs'][prev_state][action][reaction] +=1


    def getSARSAOptimizedPolicy(self, epsilon, iterations):
        current_policy = self.vars['OPTIMAL_POLICY'].copy()
        Q = copy.deepcopy(self.vars['Q'])
        P = self.vars['transitionProbs']

        #simulation of several episodes
        print "Optimizing using SARSA"
        for i in range(iterations):
            ignoreATSOPDead, ignoreSDDead = False, False
            #episode
            s0 = 1
            action0 = decideAction(current_policy[s0], setupVars.vars['ACTIONS'], epsilon)
            while s0 != 1000:
                reaction = weighted_choice([(r,v)  for r,v in P[s0][action0].iteritems() if r!='obs'])
                reward = setupVars.vars['REACTION_REWARD'][action0][reaction]
                s1 = getNewCell(s0, reaction)
                if s1 ==s0:
                    if reaction == 'down':
                        if not ignoreATSOPDead:
                            ignoreATSOPDead = True
                        else:
                            continue

                    elif reaction == 'right':
                        if not ignoreSDDead:
                            ignoreSDDead = True
                        else:
                            continue
                    else:
                        continue

                if s1!=s0 and ignoreSDDead == True:
                    ignoreSDDead = False
                if s1!=s0 and ignoreATSOPDead == True:
                    ignoreATSOPDead = False

                action1 = decideAction(current_policy[s1], setupVars.vars['ACTIONS'], epsilon)

                Q[s0][action0] = Q[s0][action0] + setupVars.vars['ALPHA'] * (reward + setupVars.vars['GAMMA']* Q[s1][action1] - Q[s0][action0])
                # print s0, '-->', s1
                s0 = s1
                action0 = action1
            # print '------------------'

        current_policy, V  = optimizePolicy(Q)
        self.vars['OPTMAL_Q'] = Q
        self.vars['OPTIMAL_V'] = V

    def readyForSARSA(self):
        # print set(self.vars['Q'].keys()) - set([1000]) - set(self.observation.keys())
        return len(set(self.vars['Q'].keys()) - set([1000]) - set(self.observation.keys()) ) == 0

def decideAction(action,actions, epsilon):
    # epsilon / len(actions) to all and 1-epsilon to action additional
    weights = [(a, [epsilon/len(actions), 1- epsilon + epsilon/len(actions) ][a==action]) for a in actions]
    return weighted_choice(weights)

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
          return c
      upto += w
   assert False, "Shouldn't get here"

def optimizePolicy(Q):
    policy = {}
    V = {}
    for cell in Q:
        _max =  max(Q[cell].iteritems(), key= lambda x:x[1])
        V[cell] = _max[1]
        policy[cell] = _max[0]
    return policy, V


def getNewCell(s,reaction):
    if reaction == 'dead':
        return 1000

    if s % setupVars.vars['MAX_ATSOP_ROWS'] == 0:
        if reaction == 'down':
            return s

    if 1 + (s-1)/setupVars.vars['MAX_ATSOP_ROWS'] >= setupVars.vars['MAX_SD_COLS']:
        if reaction == 'right':
            return s

    if reaction == 'right':
        return s + setupVars.vars['MAX_ATSOP_ROWS']

    if reaction == 'down':
        return s + 1



import random
app = Flask(__name__)
sockets = Sockets(app)

setupVars = setup()
userData =  userSourceData()
segmentObjects = segmentData()

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('landingPage.html', direct = userData.source['direct'],\
    search = userData.source['search'],  social = userData.source['social'])

@app.route('/initiateSession', methods=['GET','POST'])
def initSession():
    source = request.json['source']
    userData.recordSource(source)
    userData.currentSource = source
    return str(url_for('home'))

@app.route('/mdp_setup', methods=['GET', 'POST'])
def mdp_setup():
    return render_template('mdp_index2.html')

@app.route('/getNews', methods=['GET', 'POST'])
def getNews():
    return jsonify(news['news'])

@app.route('/loadSetup', methods=['POST'])
def loadSetup():
    print "\nSetting up parameters ... \n"

    userData.__init__()

    setupVars.vars = {}
    for segment in  ['direct','search','social']:
        segmentObjects.vars[segment] = learnedObjectsVars()


    data = request.json

    ACTIONS = data['action'].keys()
    REACTION_REWARD = {x:{y:float(v) for y,v in data['action'][x].iteritems() if y!= 'use_rate' } for x in data['action']}
    USED_POLICY = {x:[float(v) for y,v in data['action'][x].iteritems() if y== 'use_rate'][0]  for x in data['action'] }

    # normalize policy
    total = sum(USED_POLICY.values())
    USED_POLICY = {x:v/total for x,v in USED_POLICY.iteritems()}

    setupVars.vars['ACTIONS']  = ACTIONS
    setupVars.vars['REACTION_REWARD'] = REACTION_REWARD
    setupVars.vars['USED_POLICY'] = USED_POLICY
    setupVars.vars['MAX_ATSOP_ROWS'] = int(data['params']['MAX_ATSOP_ROWS'])
    setupVars.vars['MAX_SD_COLS'] = int(data['params']['MAX_SD_COLS'])
    setupVars.vars['ATSOP_GAP'] = int(data['params']['ATSOP_GAP'])
    setupVars.vars['GAMMA'] =float(data['params']['GAMMA'])
    setupVars.vars['ALPHA'] =float(data['params']['ALPHA'])

    setupVars.save()

    ncells = setupVars.vars['MAX_ATSOP_ROWS'] * setupVars.vars['MAX_SD_COLS']

    ncells = [x for x in range(ncells)] + [999]
    for segment in  ['direct','search','social']:
        learnedObjects = learnedObjectsVars()
        Q = {x+1:{x:0.0 for x in ACTIONS} for x in ncells}
        EXECUTED_POLICY = {x+1:{x:0.0 for x in ACTIONS} for x in ncells}

        learnedObjects.vars['Q'] = Q
        learnedObjects.vars['OPTIMAL_POLICY'] = {x+1:'n' for x in ncells}
        learnedObjects.vars['V'] = {x+1: 0 for x in ncells}
        learnedObjects.vars['EXECUTED_POLICY'] = EXECUTED_POLICY
        learnedObjects.vars['pages'] =defaultdict(dict)
        learnedObjects.vars['transitionProbs'] = {x+1:{action:{'obs':3,'down':1,'right':1,'dead':1 } for action in setupVars.vars['ACTIONS']} for x in ncells }

        # learnedObjects.save()
        segmentObjects.vars[segment] = learnedObjects

    return str(url_for('welcome'))

@app.route('/loadHome', methods=['GET'])
def home():
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        user_data[cookie] = {'atsop_mean': 150000, 'sd_mean':5, 'catsop':150000, 'visits':1}

    json.dump( user_data,open('userData.json','w'))

    data = user_data[cookie]
    categories = news['news'].keys()
    # parameters = json.loads(open('./static/parameters.json').read())
    return render_template('index.html', news=news['news'], categories = categories)

@app.route('/feedback', methods=['POST'])
def updates():
    learnedObjects = segmentObjects.vars[userData.currentSource]

    ignoreDead = False
    data = request.json # it has prev_state,next_state, action, reaction
    print data
    # update Q
    nobs = len(data['feedback1'])
    for x,i in enumerate(data['feedback1']):

        # there are thre cases -  dot at atsop boundary ; dot at sd boundary; dot at the corner
        # in first two the 2nd last will satisfy the condition below.
        # last one might have thrid last and second last with same next and prev state
        # in that case it will update using  third observation but satidfy the condition below
        # at the second last and ignore the dead state will be ignored
        if i['prev_state'] == i['next_state'] and x == nobs-2 :
            ignoreDead = True

        if x == nobs -1  and ignoreDead:
            continue

        learnedObjects.updateQ(i['prev_state'], i['next_state'], i['action'],i['reaction'])
        learnedObjects.recordPolicy(i['prev_state'], i['action'])
        learnedObjects.recordPageValue(i['url'], i['reaction'], i['action'],i['SD'])
        learnedObjects.recordTransitionProbs(i['prev_state'], i['action'], i['reaction'])
        learnedObjects.updateV(i['prev_state'], i['next_state'], i['action'],i['reaction'])

    # find out optimal policy & find out V
    learnedObjects.updateVandPolicy()


    if learnedObjects.readyForSARSA():
        print "SARSA"
        learnedObjects.getSARSAOptimizedPolicy(0.3,1000)

    setupVars.save()
    learnedObjects.save()

    return "sdf"

@app.route('/getQ')
def getQ():
    total = {}
    # convert the Q dictionary in the format of heatmap
    for segment in ['direct','search','social']:
        out = defaultdict(list)
        for a in setupVars.vars['ACTIONS']:
            learnedObjects = segmentObjects.vars[segment]
            for i in learnedObjects.vars['Q']:
                if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                    row = [ learnedObjects.vars['Q'][i+x*setupVars.vars['MAX_ATSOP_ROWS']][a]  for x in range(setupVars.vars['MAX_SD_COLS'])]
                    out[a].append(row)
                else:
                    break
            out[a] = out[a][::-1] # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
        total[segment] = out
    return jsonify(total)

@app.route('/getV')
def getV():
    total = {}
    for segment in ['direct','search','social']:
        out = []
        learnedObjects = segmentObjects.vars[segment]
        for i in learnedObjects.vars['V']:
            if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                row = [ learnedObjects.vars['V'][i+x*setupVars.vars['MAX_ATSOP_ROWS']] for x in range(setupVars.vars['MAX_SD_COLS'])]
                out.append(row)
            else:
                break
        value = out[0][0]
        out = out[::-1] # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
        total[segment] = {'V' :out, 'value':value, 'similarity': userData.getSimilarity(segment) }
    return jsonify(total)

@app.route('/getPolicy')
def getPolicy():
    total = {}
    for segment in ['direct','search','social']:
        learnedObjects  = segmentObjects.vars[segment]
        SARSA = learnedObjects.readyForSARSA()

        out1,out2 = [],[]
        actions = {x[0]:e for e,x in enumerate(setupVars.vars['ACTIONS'])}

        for i in learnedObjects.vars['V']:
            if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                tmp1,tmp2 = [],[]
                for x in range(setupVars.vars['MAX_SD_COLS']):
                    a  = learnedObjects.vars['OPTIMAL_POLICY'][i+x*setupVars.vars['MAX_ATSOP_ROWS']]

                    tmp1.append(actions[a[0]])
                    tmp2.append(a[0])

                out1.append(tmp1)
                out2.append(tmp2)
            else:
                break
        out1,out2 = out1[::-1], out2[::-1]
        # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
        total[segment] = {'policy' :out2, 'number':out1, 'SARSA':SARSA}
    return jsonify(total)

@app.route('/getUsedPolicy')
def getUsedPolicy():
    total = {}
    for segment in ['direct','search','social']:
        learnedObjects  = segmentObjects.vars[segment]
        p = learnedObjects.vars['EXECUTED_POLICY'].copy()
        #normalize
        for i in p:
            total_ = sum(p[i].values())
            if total_ ==0:
                p[i] = ('?/','?')
                continue
            _max= max(p[i].iteritems(), key=lambda x:x[1])
            p[i] = (_max[0], round(1.0*_max[1]/total_,1))

        out1,out2 = [],[]
        actions = {x[0]:e for e,x in enumerate(setupVars.vars['ACTIONS'])}
        actions['?'] = 4
        for i in learnedObjects.vars['V']:
            if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                tmp1,tmp2 = [],[]
                for x in range(setupVars.vars['MAX_SD_COLS']):
                    a  = p[i+x*setupVars.vars['MAX_ATSOP_ROWS']]
                    tmp1.append(actions[a[0][0]])
                    tmp2.append(str(a[0][0])+" "+ str(a[1]))

                out1.append(tmp1)
                out2.append(tmp2)
            else:
                break
        out1,out2 = out1[::-1], out2[::-1]
        # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
        total[segment] = {'policy' :out2, 'number':out1}
    return jsonify(total)

@app.route('/getPages')
def getPages():
    total = {}
    for segment in ['direct','search','social']:
        learnedObjects  = segmentObjects.vars[segment]
        out = defaultdict(dict)
        pages = learnedObjects.vars['pages']
        actions = setupVars.vars['ACTIONS']
        for i in pages:
            for sd in pages[i]:
                out[i][sd]  = {action: round(1.0*pages[i][sd][action]['sum']/ (1+pages[i][sd][action]['obs']),2) for action in actions}
        total[segment] = {'pages': out }

    return jsonify(total)

@app.route('/getOptV')
def getOptV():
    total = {}
    for segment in ['direct','search','social']:
        learnedObjects  = segmentObjects.vars[segment]
        out = [[0 for x in range(setupVars.vars['MAX_SD_COLS'])] for y in  range(setupVars.vars['MAX_ATSOP_ROWS']) ]
        if learnedObjects.readyForSARSA():
            out  = []
            for i in learnedObjects.vars['OPTIMAL_V']:
                if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                    row = [ learnedObjects.vars['OPTIMAL_V'][i+x*setupVars.vars['MAX_ATSOP_ROWS']] for x in range(setupVars.vars['MAX_SD_COLS'])]
                    out.append(row)
                else:
                    break
            out =  out[::-1] # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
        # print out
        total[segment] = {'OptV' :out}
    return jsonify(total)

if __name__ == "__main__":
    news = {'news': json.load(open('./static/news.json'))}
    user_data = json.load(open('userData.json'))

    app.run('0.0.0.0', 9090, debug=True)
