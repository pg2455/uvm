from flask import Response, Flask, request, jsonify, render_template, make_response, url_for,redirect, send_from_directory
import json

app = Flask(__name__)
user_data = json.load(open('userData.json'))

@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('landingPage.html')

@app.route('/loadHome', methods=['GET'])
def home():
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        user_data[cookie] = {'atsop_mean': 150000, 'sd_mean':5, 'catsop':150000, 'visits':1}

    json.dump( user_data,open('userData.json','w'))

    data = user_data[cookie]
    categories = news['news'].keys()
    return render_template('index.html', news=news['news'], data=data, categories = categories)

@app.route('/getNews', methods=['GET', 'POST'])
def getNews():
    return jsonify(news['news'])

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    cookie = request.headers['Cookie']
    if cookie not in user_data:
        return redirect(url_for('home'))

    print data
    user_data[cookie]['atsop_mean'] = 1.0*(user_data[cookie]['atsop_mean']*user_data[cookie]['visits'] + \
        sum(data['times']))/(user_data[cookie]['visits'] + 1)
    user_data[cookie]['sd_mean'] = 1.0*(user_data[cookie]['sd_mean']*user_data[cookie]['visits'] + \
        len(data['times']))/(user_data[cookie]['visits'] + 1)
    user_data[cookie]['catsop'] = user_data[cookie]['catsop'] + sum(data['times'])
    user_data[cookie]['visits'] +=1

    json.dump( user_data,open('userData.json','w'))

    return "d"

if __name__ == "__main__":
    news = json.load(open('./static/news.json'))

    user_data = json.load(open('userData.json'))
    app.run('0.0.0.0', 9090, debug=True)
