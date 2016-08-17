from flask import Response, Flask, request, jsonify, render_template, make_response, url_for,redirect, send_from_directory
import json

from MDP_functions import * # update Q and track policy

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
    ACTIONS = data.keys()
    REACTION_REWARD = {x:{y:float(v) for y,v in data[x].iteritems() if y!= 'use_rate' } for x in data}
    USED_POLICY = {x:[float(v) for y,v in data[x].iteritems() if y== 'use_rate'][0]  for x in data }
    # normalize policy
    total = sum(USED_POLICY.values())
    USED_POLICY = {x:v/total for x,v in USED_POLICY.iteritems()}

    parameters = json.loads(open('./static/parameters.json').read())
    parameters['ACTIONS'] = ACTIONS
    parameters['REACTION_REWARD'] = REACTION_REWARD
    parameters['USED_POLICY'] = USED_POLICY

    Q = {x+1:getActionDict(ACTIONS) for x in range(parameters['MAX_ATSOP_ROWS']*parameters['MAX_SD_COLS'])}
    EXECUTED_POLICY = {x+1:getActionDict(ACTIONS) for x in range(parameters['MAX_ATSOP_ROWS']*parameters['MAX_SD_COLS'])}
    parameters['Q'] = Q
    parameters['EXECUTED_POLICY']=EXECUTED_POLICY
    json.dump(parameters,open('./static/parameters.json', 'w'))

    writeToParametersJS(parameters)

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
    return render_template('index.html', news=news['news'], rewards = json.dumps(parameters['REACTION_REWARD']),\
     categories = categories, actions = parameters["ACTIONS"], prob = json.dumps(parameters["USED_POLICY"]))


@app.route('/feedback', methods=['POST'])
def updates():
    data = request.json
    print data
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        return redirect(url_for('home'))

    parameters = json.loads(open('./static/parameters.json').read())
    Q = updateQ(parameters['Q'],parameters['REACTION_REWARD'], str(data['prev_state']), str(data['next_state']), data['action'],data['reaction'], parameters['ALPHA'], parameters['GAMMA'])
    parameters['Q'] = Q
    json.dump(parameters,open('./static/parameters.json', 'w'))
    print Q
    return "d"


if __name__ == "__main__":
    news = json.load(open('./static/news.json'))

    user_data = json.load(open('userData.json'))
    app.run('0.0.0.0', 9090, debug=True)
