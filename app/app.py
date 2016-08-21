from flask import Response, Flask, request, jsonify, render_template, make_response, url_for,redirect, send_from_directory
import json
# from flask.ext.socketio import SocketIO, emit
from collections import defaultdict
from flask_sockets import Sockets

class setup(object):
    def __init__(self):
        self.vars = {}

    def save(self):
        json.dump(self.vars,open('./static/parameters.json', 'w'))

class learnedObjectsVars(object):
    def __init__(self):
        self.vars = {}

    def save(self):
        json.dump(self.vars,open('./static/learnedObjects.json', 'w'))

    def updateQ(self, prev_state, next_state, action, reaction):
        # update equation
        Q = self.vars['Q'] # it makes a copy
        Q[prev_state][action] = Q[prev_state][action] + \
                    setupVars.vars['ALPHA'] *( setupVars.vars['REACTION_REWARD'][action][reaction] + setupVars.vars['GAMMA']* max(Q[next_state].itervalues()) - Q[prev_state][action] )

    def recordPolicy(self, prev_state, action):
        self.vars['EXECUTED_POLICY'][prev_state][action]+=1

    def updateVandPolicy(self):
        Q = self.vars['Q'] # it makes a copy of the name and not create a new object
        V = self.vars['V']
        policy = self.vars['OPTIMAL_POLICY']

        for i in V:
            _max =  max(Q[i].iteritems(), key= lambda x:x[1])
            V[i] = _max[1]
            policy[i] = _max[0]

    def recordPageValue(self, url, prev_state, next_state, action):
        if url not in self.vars['pages']:
            self.vars['pages'][url] = {a:0 for a in setupVars.vars['ACTIONS']}

        self.vars['pages'][url][action] += self.vars['V'][next_state] - self.vars['V'][prev_state]

setupVars = setup()
learnedObjects = learnedObjectsVars()

from MDP_functions import * # update Q and track policy

import random
app = Flask(__name__)
sockets = Sockets(app)

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('landingPage.html')

@app.route('/mdp_setup', methods=['GET', 'POST'])
def mdp_setup():
    return render_template('mdp_index.html')

@app.route('/getNews', methods=['GET', 'POST'])
def getNews():
    return jsonify(news['news'])

@app.route('/loadSetup', methods=['POST'])
def loadSetup():
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
    Q = {x+1:getActionDict(ACTIONS) for x in ncells}
    EXECUTED_POLICY = {x+1:getActionDict(ACTIONS) for x in ncells}

    learnedObjects.vars['Q'] = Q
    learnedObjects.vars['OPTIMAL_POLICY'] = {x+1:'n' for x in ncells}
    learnedObjects.vars['V'] = {x+1: 0 for x in ncells}
    learnedObjects.vars['EXECUTED_POLICY'] = EXECUTED_POLICY
    learnedObjects.vars['pages'] =defaultdict(dict)

    learnedObjects.save()

    return str(url_for('welcome'))

@app.route('/loadHome', methods=['GET'])
def home():
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        user_data[cookie] = {'atsop_mean': 150000, 'sd_mean':5, 'catsop':150000, 'visits':1}

    json.dump( user_data,open('userData.json','w'))

    data = user_data[cookie]
    categories = news['news'].keys()
    parameters = json.loads(open('./static/parameters.json').read())
    return render_template('index.html', news=news['news'], categories = categories)

@app.route('/feedback', methods=['POST'])
def updates():
    data = request.json # it has prev_state,next_state, action, reaction
    print data['feedback']

    # update Q
    for i in data['feedback']:
        learnedObjects.updateQ(i['prev_state'], i['next_state'], i['action'],i['reaction'])
        learnedObjects.recordPolicy(i['prev_state'], i['action'])
        learnedObjects.recordPageValue(i['url'], i['prev_state'], i['next_state'], i['action'])

    # find out optimal policy & find out V
    learnedObjects.updateVandPolicy()

    setupVars.save()
    learnedObjects.save()

    return "sdf"

@app.route('/getQ')
def getQ():
    out = defaultdict(list)

    # convert the Q dictionary in the format of heatmap
    for a in setupVars.vars['ACTIONS']:
        for i in learnedObjects.vars['Q']:
            if i <= setupVars.vars['MAX_ATSOP_ROWS']:
                row = [ learnedObjects.vars['Q'][i+x*setupVars.vars['MAX_ATSOP_ROWS']][a]  for x in range(setupVars.vars['MAX_SD_COLS'])]
                out[a].append(row)
            else:
                break
        out[a] = out[a][::-1] # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
    return jsonify(out)

@app.route('/getV')
def getV():
    out = []
    for i in learnedObjects.vars['V']:
        if i <= setupVars.vars['MAX_ATSOP_ROWS']:
            row = [ learnedObjects.vars['V'][i+x*setupVars.vars['MAX_ATSOP_ROWS']] for x in range(setupVars.vars['MAX_SD_COLS'])]
            out.append(row)
        else:
            break
    out = out[::-1] # so that heatpmap is displayed top(0s) to bottom(max number fof seconds)
    return jsonify({'V' :out})

@app.route('/getPolicy')
def getPolicy():
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
    return jsonify({'policy' :out2, 'number':out1})

@app.route('/getUsedPolicy')
def getUsedPolicy():
    p = learnedObjects.vars['EXECUTED_POLICY'].copy()
    #normalize
    for i in p:
        total = sum(p[i].values())
        _max= max(p[i].iteritems(), key=lambda x:x[1])
        p[i] = (_max[0], round(1.0*_max[1]/(1+total),1))

    out1,out2 = [],[]
    actions = {x[0]:e for e,x in enumerate(setupVars.vars['ACTIONS'])}
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
    return jsonify({'policy' :out2, 'number':out1})

@app.route('/getPages')
def getPages():
    return jsonify({'pages': learnedObjects.vars['pages']})

if __name__ == "__main__":
    news = {'news': json.load(open('./static/news.json'))}
    user_data = json.load(open('userData.json'))

    app.run('0.0.0.0', 9090, debug=True)
