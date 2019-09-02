#!/usr/bin/env python

# Manipulate sys.path to be able to import rivescript from this local git
# repository.
import os
import sys
from pprint import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from flask import Flask, request, Response, jsonify, make_response
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

myDB = mysql.connector.connect(
        host="192.185.129.43",
        port=3306,
        user="pankagei_pkj",
        passwd="Snehapkj1989",
        db="pankagei_ann_db")

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
    # pprint(params)
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

    bot.set_subroutine("fetch_patient_data", fetch_patient_data)
    bot.set_subroutine("fetch_rupture_criticality", fetch_rupture_criticality)
    # Get a reply from the bot.
    reply = bot.reply("username", params['queryResult']['queryText'])

    # Get all the user's vars back out of the bot to include in the response.
    uservars = bot.get_uservars("username")
    print("print(reply) ", reply)
    # Send the response.
    return make_response(jsonify({'fulfillmentText':reply}))

def fetch_patient_data(rs, args):
    resp = "There are about " + str(query_db(extract_args(args))) + " patients like that."
    return resp

def calc_percentage(part, whole):
  return 100 * float(part)/float(whole)

def fetch_rupture_criticality(rs, args):
    query = ""
    for s in args:
        query += s + " "
    # print(query)
    args_dict = {}
    for s in query.split('and'):
        print(s)
        args_dict[s.split('is')[0].strip()] = s.split('is')[1].strip()
    pprint(args_dict)
    rup_prob = query_db_rup1(args_dict)
    if(rup_prob == 0):
        resp = "Could not calculate the rupture probability for the given input."
    else:
        resp = "The rupture probablity for this patient is about " + str(rup_prob) + "%"
    print("print(resp) ", resp)
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
            arg1 = firsttwo.replace(" ", "_")
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
            arg1 = firsttwo.replace(" ", "_")
            arg2 = secondtwo
        elif firstthree in pat_feats:
            arg1 = firstthree.replace(" ", "_")
            arg2 = args[3]
        else:
            arg1 = args[0]
            arg2 = secondthree
    return arg1, arg2

def query_db(args):
    mycursor = myDB.cursor(prepared=True)
    query = """SELECT COUNT(*) FROM `ann_data` WHERE %s LIKE '%s'""" % (args[0], "%" + args[1] + "%")  
    print(query)
    mycursor.execute(query)
    myresult = mycursor.fetchone()
    for x in myresult:
        print(x)
    return myresult[0]

def query_db_rup(args_dict):
    mycursor = myDB.cursor(prepared=True)
    query_sel_template = """SELECT `probability` FROM `ann_rup_prob` """
    query_where_template = """ WHERE `location` LIKE %s 
    AND `size` LIKE %s 
    AND `rule_1` LIKE %s 
    AND `rule_2` LIKE %s"""
    arg_r1 = 'gender_' + args_dict['gender']
    arg_r2 = 'motor_deficits_' + args_dict['motor deficits']
    query = query_sel_template + query_where_template % ("'" + args_dict['aneurysm location'] + "'", 
    "'" + args_dict['size category'] + "'", "'" + arg_r1 + "'", "'" + arg_r2 + "'")  
    print(query)
    mycursor.execute(query)
    result = mycursor.fetchone()
    pprint(result)
    if(result is None):
        return 0
    else:
        return calc_percentage(result[0].decode(), 10)

def query_db_rup1(args_dict):
    mycursor = myDB.cursor(prepared=True)
    query_sel_template = """SELECT `probability` FROM `ann_rup_prob` """
    query_where_template = """ WHERE `location` LIKE %s 
    AND `size` LIKE %s 
    AND `rule_1` LIKE %s 
    AND `rule_2` LIKE %s"""

    args=[]
    for key in args_dict:
        if('location' in key or 'size' in key):
            continue
        else:
            args.append(key.replace(' ', '_') + "_" + args_dict[key].replace(' ', '_'))

    print(args)

    query = query_sel_template + query_where_template % ("'" + args_dict['aneurysm location'] + "'", 
    "'" + args_dict['size'] + "'", "'" + args[0] + "'", "'" + args[1] + "'")  

    print(query)
    
    mycursor.execute(query)
    result = mycursor.fetchone()
    pprint(result)
    if(result is None):
        return 0
    else:
        return calc_percentage(result[0].decode(), 10)

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