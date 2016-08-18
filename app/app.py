from flask import Response, Flask, request, jsonify, render_template, make_response, url_for,redirect, send_from_directory
import json
# from flask.ext.socketio import SocketIO, emit
from collections import defaultdict
from MDP_functions import * # update Q and track policy

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


setupVars = setup()
learnedObjects = learnedObjectsVars()

import random
app = Flask(__name__)

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

    Q = {x+1:getActionDict(ACTIONS) for x in range( ncells )}
    EXECUTED_POLICY = {x+1:getActionDict(ACTIONS) for x in range( ncells )}

    learnedObjects.vars['Q'] = Q
    learnedObjects.vars['OPTIMAL_POLICY'] = {x+1:getActionDict(ACTIONS) for x in range(ncells)}
    learnedObjects.vars['V'] = {x+1: 0 for x in range(ncells)}
    learnedObjects.vars['ExecutedPolicy'] = EXECUTED_POLICY

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
    data = request.json
    print data
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        return redirect(url_for('home'))

    Q = updateQ(parameters['Q'],parameters['REACTION_REWARD'], str(data['prev_state']), str(data['next_state']), data['action'],data['reaction'], parameters['ALPHA'], parameters['GAMMA'])
    parameters['Q'] = Q
    json.dump(parameters,open('./static/parameters.json', 'w'))
    print Q
    return "d"


@app.route('/statusUpdate')
def statusUpdate():
    print request.json
    return " "

@app.route('/getQ')
def getQ():
    out = defaultdict(list)
    actions = setupVars.vars['ACTIONS']
    MAX_ATSOP_ROWS = setupVars.vars['MAX_ATSOP_ROWS']
    MAX_SD_COLS = setupVars.vars['MAX_SD_COLS']
    Q = learnedObjects.vars['Q']

    # convert the Q dictionary in the format of heatmap
    for a in actions:
        for i in Q:
            if i <= MAX_ATSOP_ROWS:
                row = [ Q[i+x*MAX_ATSOP_ROWS][a] + random.random() for x in range(MAX_SD_COLS)]
                out[a].append(row)
            else:
                break
    return jsonify(out)


if __name__ == "__main__":
    news = json.load(open('./static/news.json'))

    user_data = json.load(open('userData.json'))
    app.run('0.0.0.0', 9090, debug=True)
