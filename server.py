#!/usr/bin/env python

# Manipulate sys.path to be able to import rivescript from this local git
# repository.
import os
import sys
from pprint import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from flask import Flask, request, Response, jsonify
import json
from rivescript import RiveScript
import mysql.connector

# Set up the RiveScript bot. This loads the replies from `/eg/brain` of the
# git repository.
bot = RiveScript()
bot.load_directory(
    os.path.join(os.path.dirname(__file__), "", "brain")
)

bot.sort_replies()

app = Flask(__name__)

@app.route("/reply", methods=["POST"])
def reply():
    """Fetch a reply from RiveScript.
    Parameters (JSON):
    * username
    * message
    * vars
    """
    params = request.json
  
    if not params:
        return jsonify({
            "status": "error",
            "error": "Request must be of the application/json type!",
        })

    # username = params.get("username")
    # message  = params.get("message")
    # uservars = params.get("vars", dict())

    # Make sure the required params are present.
    # if username is None or message is None:
    #     return jsonify({
    #         "status": "error",
    #         "error": "username and message are required keys",
    #     })

    # Copy and user vars from the post into RiveScript.
    # if type(uservars) is dict:
    #     for key, value in uservars.items():
    #         bot.set_uservar(username, key, value)

    bot.set_subroutine("hello_world", hello_world)
    # Get a reply from the bot.
    reply = bot.reply("username", params['queryResult']['queryText'])

    # Get all the user's vars back out of the bot to include in the response.
    uservars = bot.get_uservars("username")
    
    # Send the response.
    return jsonify({
      "fulfillmentText": "This is a text response",
      "fulfillmentMessages": [
        {
          "card": {
            "title": "card title",
            "subtitle": "card text",
            "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
            "buttons": [
              {
                "text": "button text",
                "postback": "https://assistant.google.com/"
              }
            ]
          }
        }
      ],
      "source": "example.com",
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "this is a simple response"
                }
              }
            ]
          }
        },
        "facebook": {
          "text": "Hello, Facebook!"
        },
        "slack": {
          "text": "This is a text response for Slack."
        }
      },
      "outputContexts": [
        {
          "name": "projects/quotebot-18fe7/agent/sessions/69702c65-2e06-d2fa-0225-75bd0381bdc9/contexts/context name",
          "lifespanCount": 5,
          "parameters": {
            "param": "param value"
          }
        }
      ],
      "followupEventInput": {
        "name": "event name",
        "languageCode": "en-US",
        "parameters": {
          "param": "param value"
        }
      }
    })

def hello_world(rs, args):
    resp = "There are about " + str(query_db(extract_args(args))) + " patients like that."
    return resp

def extract_args(args):
    pat_feats = ['gender','age','race','speech deficits','motor deficits','sensory deficits','diabetes', 
    'hypertension','heart disease','copd','polycystic kidney disease','smoking habit','cigarettes','cigar',
    'smokeless','number of aneurysms','multiple aneurysms','family history','spinning feeling','dizziness', 
    'diplopia','blurred vision','location','region','size','side','symptomatic']
    pat_feats_vals = ['male','female','current smoker']
    arg1 = ""
    arg2 = ""
    if len(args) == 2:
        arg1 = args[0]
        arg2 = args[1]
    elif len(args) == 3:
        firsttwo = args[0] + " " +  args[1]
        secondtwo = args[1] + " " +  args[2]
        if firsttwo in pat_feats:
            arg1 = firsttwo
            arg2 = args[2]
        else:
            arg1 = args[0]
            arg2 = secondtwo
    elif len(args) == 4:
        firsttwo = args[0] + " " + args[1]
        secondtwo = args[2] + " " +  args[3]
        firstthree = args[0] + " " +  args[1] + " " +  args[2]
        secondthree = args[1] + " " +  args[2] + " " +  args[3]
        if firsttwo in pat_feats:
            arg1 = firsttwo
            arg2 = secondtwo
        elif firstthree in pat_feats:
            arg1 = firstthree
            arg2 = args[3]
        else:
            arg1 = args[0]
            arg2 = secondthree
    return arg1, arg2

def query_db(args):
    myDB = mysql.connector.connect(
        host="192.185.129.43",
        port=3306,
        user="pankagei_pkj",
        passwd="Snehapkj1989",
        db="pankagei_ann_db")
    mycursor = myDB.cursor(prepared=True)
    query = """SELECT COUNT(*) FROM `ann_data` WHERE %s LIKE '%s'""" % (args[0], args[1])  
    print(query)
    mycursor.execute(query)
    myresult = mycursor.fetchone()
    for x in myresult:
        print(x)
    return myresult[0]

@app.route("/")
@app.route("/<path:path>")
def index(path=None):
    """On all other routes, just return an example `curl` command."""
    payload = {
        "username": "soandso",
        "message": "Hello bot",
        "vars": {
            "name": "Soandso",
        }
    }
    return Response(r"""Usage: curl -i \
    -H "Content-Type: application/json" \
    -X POST -d '{}' \
    http://localhost:5000/reply""".format(json.dumps(payload)),
    mimetype="text/plain")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)