########### Python 2.7 #############
import httplib, urllib, base64


def getNews(category):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': 'ce9f46b167f24be4af64bec952f6976d',
    }

    params = urllib.urlencode({
        # Request parameters
        'Category': category,
    })

    try:
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/news/?%s" % params ,"{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


categories = ['Business', 'Entertainment', 'Health', 'Politics', 'ScienceAndTechnology', 'Sports', 'US/UK', 'World']

news = {}
for category in categories:
    news[category] = eval(getNews(category));

import json
json.dump(news, open('news.json','w'))
