#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

from pymongo import MongoClient

# Flask app should start in global layout
app = Flask(__name__)

#Connecting to MongoDB
client = MongoClient("mongodb://dbuser:dbuser@ds137336.mlab.com:37336/headcountdb")
db = client.headcountdb


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "roll-off.date":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    emp_id = parameters.get("Employee_Id")

    speech = executeQueryInDB(emp_id)

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-headcount-report"
    }

def executeQueryInDB(emp_id):
    if emp_id:
        headCountColl = db.HeadCountColl
        results = headCountColl.find_one({"Personnel No": int(emp_id)})
        speech = "Roll-off Date for {employee_id} is {roll_off_date}".format(employee_id = emp_id, roll_off_date = results['Roll-Off date'])

    return speech


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
