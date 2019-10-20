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
from models.SubPreObj import SubPreObj
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
# Set up the RiveScript bot. This loads the replies from `/eg/brain` of the
# git repository.
bot = RiveScript()
bot.load_directory(
    os.path.join(os.path.dirname(__file__), "", "rivescript_brain")
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
    print("User Query: ", params['queryResult']['queryText'])
    # Get a reply from the bot.
    reply = bot.reply("user_1", params['queryResult']['queryText'])

    # Get all the user's vars back out of the bot to include in the response.
    uservars = bot.get_uservars("user_1 ")
    # print("print(reply) ", reply)
    # Send the response.
    return make_response(jsonify({'fulfillmentText':reply}))

def fetch_patient_data(rs, args):
    patient_count = query_db(extract_args(args))
    if patient_count == 0:
        resp = "There are no patients like that. Is there anything else I can help you with?"
    elif patient_count == 1:
        resp = "There is " + str(patient_count) + " patient like that. Is there anything else I can help you with?"
    else:
        resp = "There are about " + str(patient_count) + " patients like that. Is there anything else I can help you with?"
    return resp

def calc_percentage(part, whole):
  return 100 * float(part)/float(whole)

# def fetch_rupture_criticality(rs, args):
#     query = ""
#     for s in args:
#         query += s + " "
#     # print(query)
#     args_dict = {}
#     for s in query.split('and'):
#         print(s)
#         args_dict[s.split('is')[0].strip()] = s.split('is')[1].strip()
#     pprint(args_dict)
#     rup_prob = query_db_rup1(args_dict)
#     if(rup_prob == 0):
#         resp = "Could not calculate the rupture probability for the given input."
#     else:
#         resp = "The rupture probablity for this patient is about " + str(rup_prob) + "%"
#     print("print(resp) ", resp)
#     return resp

# def fetch_rupture_criticality(rs, args):
#     print('===============\n', 'IDENTIFIED VARS')
#     for key in rs.get_uservars('user_1'):
#         if('__lastmatch__' in key or 'topic' in key or '__history__' in key):
#             continue
#         else:
#             print(key, " : ", rs.get_uservar('user_1',key))
#             # pprint(rs.get_uservars(key))
#     print('===============')
#     resp="Thanks!"
#     return resp

def find_age_mapping(obj):
    size_val = int(obj)
    size_val = size_val / 10
    if(size_val <= 5):
        return "tiny"
    elif(4 <= size_val <= 8):
        return "small"
    elif(8 <= size_val <= 14):
        return "medium"
    elif(14 <= size_val <= 22):
        return "large"
    elif(size_val >= 22):
        return "giant"

def find_mapping(obj):
    if "motor" in obj:
        return "motor_deficits_yes"
    elif "smoke" in obj:
        return "smoking_history_current_smoker"
    elif "hypertension" in obj:
        return 'hypertension_yes'
    elif "multiple aneurysms" in obj:
        return 'multiple_aneurysms_yes'
    else: 
        age_val = int(obj)
        if( 38 <= age_val <= 58):
            return "age_category_generation_x"
        elif(age_val <= 37):
            return "age_category_generation_y"
        elif(age_val >= 74):
            return "age_category_silent_generation"
        elif(56 <= age_val <= 73):
            return "age_category_baby_boomers"

def map_spo_to_sql_rup(spo_list):
    loc = ''
    size = ''
    rules = []
    rem_list = ['aneurysm', 'patient', 'age']
    for spo in spo_list:
        sub = spo.sub
        obj = spo.obj
        if "location" in sub:
            loc = obj
        elif "size" in sub:
            size = find_age_mapping(obj)
        else:
            for s in rem_list:
                if s in sub:
                    sub = sub.replace(s, '')
            if(sub):
                rule = sub + ' ' + obj
                rules.append(rule.strip().replace(' ', '_'))
            else:
                rules.append(find_mapping(obj))

    sel_q = "SELECT probability FROM ann_rup_prob WHERE "
    loc_size = """location LIKE '%s' AND size LIKE '%s' """ % (loc, size)
    sql1 = sel_q + loc_size + """AND rule_1 LIKE '%s' AND rule_2 LIKE '%s' """ % (rules[0], rules[1])
    sql2 = sel_q + loc_size + """AND rule_1 LIKE '%s'   AND rule_2 LIKE '%s' """ % (rules[1], rules[0])

    print('sql1', sql1)
    print('sql2', sql2)
    return sql1, sql2
# NEW
def fetch_rupture_criticality(rs, args):
    possible_subs = ['aneurysm', 'location', 'age', 'gender', 'smoking', 
    'history', 'smoking', 'habit', 'race', 'size', 'side', 'patient']
    possible_preds = ['is', 'greater', 'over', 'under', 'less than', 'has', 'between', 'had', 'was']
    stop_words = ['what','how','of','a','an','the','me','tell','can','you','are','were', 
    'ages', 'age', 'aged', 'gender', 'genders', 'race', 'disease', 'and', 'whose', 'who', 'on']
    sub = ''
    pre = ''
    obj = ''
    spo_list = []
    if 'size' not in args or 'location' not in args: return "Size or Location of Aneurysm is missing. Please retry with the corrected query" 
    for arg in args:
        if arg == "and":
            spo_list.append(SubPreObj(sub.strip(),lemmatizer(pre.strip(), u"VERB")[0],obj.strip()))
            sub = ''
            pre = ''
            obj = ''
        if arg in possible_subs:
            sub = sub + ' ' +arg      
        elif arg in possible_preds:
            pre = pre + ' ' +arg
        elif arg in stop_words:
            continue
        else:
            obj = obj + ' ' + arg
    
    if sub or pre or obj:
        spo_list.append(SubPreObj(sub.strip(),lemmatizer(pre.strip(), u"VERB")[0],obj.strip()))

    pprint(spo_list)
    sql1, sql2 = map_spo_to_sql_rup(spo_list)
    rup_prob = query_db(sql1)
    if(rup_prob == 0):
        rup_prob = query_db(sql2)

    if rup_prob == 0:
        resp = "Sorry, I could not calculate the rupture probability. Is there anything else I can help you with?"
    else:
        rup_prob_per = calc_percentage(rup_prob.decode(), 10)
        resp = "The rupture probability for this case would be close to " + str(rup_prob_per) + "%. Is there anything else I can help you with?"
    return resp

def extract_args_common(args):
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

def extract_args(args):
    stop_words = ['what','how','of','a','an','the','me','tell','can','you','are','were', 
    'had', 'ages', 'age', 'aged', 'gender', 'genders', 'race', 'disease']
    possible_subjects = ['_age_','_gender_','_race_','_smoking_', '_disease_']
    query_types = ['percentage', 'many', 'number']
    possible_predicates = ['over', 'above', 'under', 'between']
    print(args)
    sub = ''
    pre = ''
    obj = ''
    q_type = ''
    for arg in list(args):
        if(arg in stop_words):
            args.remove(arg)
    print(args)
    for arg in list(args):
        if arg in possible_subjects:
            sub = arg
        elif arg in query_types:
            q_type = arg
        elif arg in possible_predicates:
            pre = arg
        else:
            obj = obj + ' ' + arg
    
    if(pre == ''): pre = 'eq'
    spo = SubPreObj(sub,pre,obj.strip())
    pprint(spo)
    mapped_query = map_spo_to_sql(spo, q_type)
    return mapped_query 

# Take in a SPO object and map to SQL
def map_spo_to_sql(spo, q_type):
    # sub will be the column name, pre is the condition comes after where clause and objs are the vals
    # need a mapper function to map SPO instance to SELECT FROM table WHERE {sub} {pre} {obj}
    # SQL templates
    # empty pre = LIKE
    # over pre = > under pre = <
    # if pre blank means equal
    # split between queries by to or and
    # if age query, clean up OBJ value to keep only number
    mappings = {
        "_smoking_" : "smoking_habit",
        "smoking habit" : "smoking_habit",
        "number" : "COUNT(*)",
        "many" : "COUNT(*)",
        "_age_" : "age",
        "_gender_" : "gender",
        "_race_" : "race",
        "_disease_" : "disease",
        "over" : ">",
        "under" : "<",
        "eq":"LIKE"
    }
    if "between" in spo.pre:
        args = spo.obj.split("to")
        if len(args) == 0:
            args = spo.obj.split("and")
        sel_query1 = """select %s from `ann_data` where %s between %s and %s""" % (
                mappings[q_type], mappings[spo.sub], int(args[0]), int(args[1]))
        return sel_query1
        
    try:
        if "." in spo.obj :
            val = float(spo.obj)
            obj = val
            if(mappings[spo.pre] == "LIKE"): mappings[spo.pre] = "="
            sel_query1 = """select %s from `ann_data` where %s %s %s""" % (
                mappings[q_type], mappings[spo.sub], mappings[spo.pre], obj)
        else:
            val = int(spo.obj)
            obj = val
            if(mappings[spo.pre] == "LIKE"): mappings[spo.pre] = "="
            sel_query1 = """select %s from `ann_data` where %s %s %s""" % (
                mappings[q_type], mappings[spo.sub], mappings[spo.pre], obj)
    except ValueError:
        obj = spo.obj
        sel_query1 = """select %s from `ann_data` where %s %s '%s'""" % (
            mappings[q_type], mappings[spo.sub], mappings[spo.pre], '%' + lemmatizer(obj, u'NOUN')[0] + '%')

    # sel_query1 = "select " + mappings[q_type] + "from `ann_data`" 
    # + " where " + mappings[spo.sub] + " " + mappings[spo.pre] + " %" + spo.obj + "%"
    pprint(spo)
    print(q_type)
    print(sel_query1)
    return sel_query1

def query_db(query):
    mycursor = myDB.cursor(prepared=True)
    # query = """SELECT COUNT(*) FROM `ann_data` 
    # WHERE %s LIKE '%s'""" % (args[0], "%" + args[1] + "%") 
    print(query)
    mycursor.execute(query)
    myresult = mycursor.fetchone()
    if(myresult is None):
        return 0
    else: 
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