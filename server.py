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
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from services.d2v2 import make_rules_dict
from services.SpacySimilarity import calculate_similarity
from services.SpacySimilarity import process_text
from services.RuleBasedProbablisticReasoner import combined_rupture_probability
from services.enrichment import make_terms_list
import en_core_web_md
from string import Template
from random import sample 

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
# mycursor = myDB.cursor(prepared=True)

application = app = Flask(__name__)

nlp = en_core_web_md.load()
nlp.Defaults.stop_words.remove("side")

@app.route("/reply", methods=["POST"])
def reply():
    params = request.json
    # pprint(params)
    if not params:
        return jsonify({
            "status": "error",
            "error": "Request must be of the application/json type!",
        })

    bot.set_subroutine("fetch_patient_data_better", fetch_patient_data_better)
    bot.set_subroutine("fetch_rupture_criticality", fetch_rupture_criticality)
    bot.set_subroutine("combined_rupture_criticality", combined_rupture_criticality)
    user_query = params['queryResult']['queryText']
    raw_uq = user_query.replace("_", " ")
    bot.set_uservar("user_1", "raw_uq", raw_uq)
    # Get a reply from the bot.
    reply = bot.reply("user_1", raw_uq)
    # Get all the user's vars back out of the bot to include in the response.
    uservars = bot.get_uservars("user_1 ")
    # print("print(reply) ", reply)
    # Send the response.
    return make_response(jsonify({'fulfillmentText':reply}))

def isNegated(tok):
    negations = {"no", "not", "n't", "never", "none","non"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False
def extract_np(doc):
    np_list = []
    for noun_phrase in list(doc.noun_chunks):
        noun_phrase.merge(noun_phrase.root.tag_, noun_phrase.root.lemma_, noun_phrase.root.ent_type_)
    for token in doc:
        # print(token.text, token.pos_)
        if token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
            np_list.append(token.text)
    return np_list

def populate_sql_template(query_type, sel_data, whr_data):    
    sql_templates = {
        "SELECT_QUERY" : Template('SELECT $sel_cols FROM $table_name'),
        "WHERE_CLAUSE" : Template(' $col_name $cond $col_val '),
        "WHERE_BETWN_CLAUSE" : Template(' $col_name BETWEEN $col_val_1 AND $col_val_2')
    }
    sql_query = ''
    # switch case by query type
    if(query_type == 'SEL_WITH_CONDS'):
        sql_query = sql_templates["SELECT_QUERY"].substitute(table_name=sel_data['table_name'], sel_cols=sel_data['sel_cols']) + ' WHERE'
        if len(whr_data) == 1:
            print(isinstance(whr_data[0]['col_val'], list))
            if isinstance(whr_data[0]['col_val'], list):
                sql_query = sql_query + sql_templates["WHERE_BETWN_CLAUSE"].substitute(
                col_name=whr_data[0]['col_name'], cond=whr_data[0]['cond'], col_val_1=whr_data[0]['col_val'][0], col_val_2=whr_data[0]['col_val'][1])
            else:
                sql_query = sql_query + sql_templates["WHERE_CLAUSE"].substitute(
                col_name=whr_data[0]['col_name'], cond=whr_data[0]['cond'], col_val=whr_data[0]['col_val'])
        else:
            for i, whr_cond in enumerate(whr_data): 
                if i == len(whr_data)-1:
                    sql_query = sql_query + sql_templates["WHERE_CLAUSE"].substitute(
                        col_name=whr_cond['col_name'], cond=whr_cond['cond'], col_val=whr_cond['col_val'])
                else:
                    sql_query = sql_query + sql_templates["WHERE_CLAUSE"].substitute(
                        col_name=whr_cond['col_name'], cond=whr_cond['cond'], col_val=whr_cond['col_val']) + 'and'
    return sql_query

def extract_args_better(raw_uq):
    doc = nlp(raw_uq)
    # list of table names
    table_names = ['ann_data']
    # list of column names
    column_names = ["patient","gender","age","race","speech_deficits","motor_deficits","sensory_deficits",
    "diabetes","hypertension","heart_disease","smoking_habit","family_history","spinning_feeling",
    "dizziness","diplopia","blurred_vision","aneurysm_count","symptomatic","status","type","location","size","side"]
    stop_words = ['to', 'of', 'the']
    
    mappings = {
        'patient':'patient',
        'patients':'patient',
        'case':'patient',
        'cases':'patient',
        'people':'patient',
        'smoke':'smoking_habit',
        'smoker':'smoking_habit',
        'mm':'size',
        'year old':'age',
        'years old':'age'
    }
    subs  = [tok.text for tok in doc if tok.pos_ == 'NOUN']
    verbs = [tok.lemma_ for tok in doc if tok.pos_ == 'VERB']
    adps  = [tok.lemma_ for tok in doc if tok.pos_ == 'ADP' and tok.text not in stop_words]
    nums  = [tok.text for tok in doc if tok.pos_ == 'NUM']
    np = extract_np(doc)
    print('subs', subs)
    print('verbs', verbs)
    print('adps', adps)
    print('nums', nums)
    print('np', np)
    
    return subs, verbs, adps, nums, np

def make_sql_query(subs, verbs, adps, nums, np):
    column_names = ["patient","gender","age","race","speech_deficits","motor_deficits","sensory_deficits",
    "diabetes","hypertension","heart_disease","smoking_habit","family_history","spinning_feeling",
    "dizziness","diplopia","blurred_vision","aneurysm_count","symptomatic","status","type","location","size","side"]
    cond_mappings = {
        'be':'LIKE',
        'have':'=',
        'under':'<',
        'less than':'<',
        'smaller than':'<',
        'over':'>',
        'greater than':'>',
        'above':'>',
        'more than':'>',
        'between':'BETWEEN'
    }
    table_column_map = {
        'gender':['male','female','unknown'],
        'race':['African American', 'African Americans', 'Asian', 'Asians', 'Caucasian', 'Caucasians', 'Native American', 'Native Americans'],
        'type':['Saccular'],
        'location':['Anterior Communicating Artery', 'Superaclanoid Internal Carotid Artery', 'MCA'],
        'status':['ruptured', 'un-ruptured']
    }
    col_mapping = {
        'smoker' : 'smoking_habit',
        'smoke' : 'smoking_habit',
        'non smoker' : 'smoking_habit',
        'current smoker':'smoking_habit',
        'heart disease':'heart_disease'
    }
    col = ''
    vals = []
    tabl = 'ann_data'
    cond = ''
    for sub in subs:
        if sub.lower().replace(' ', '_') in column_names:
            col = sub.replace(' ', '_')
    for n in np:
        lem = lemmatizer(n.lower(), u'NOUN')[0]
        print('lem',lem)
        if n.replace(' ', '_') in column_names:
            vals.append('%yes%')
            if not col: col = n.replace(' ', '_')
        elif lem in col_mapping and col_mapping[lem] in column_names:
            print('in',lem)
            col = col_mapping[lem]
            if 'non' in n:
                vals.append("'%no%'")
            else:
                vals.append("'%yes%'")
        else:
            for col_name, col_val in table_column_map.items():  
                if n in col_val or lemmatizer(n, u'NOUN')[0] in col_val:
                    col = col_name
                    vals.append("'%"+lemmatizer(n, u'NOUN')[0]+"%'")
    if len(adps) == 0:
        for v in verbs:
            if v in cond_mappings:
                cond = cond_mappings[v]
    else:
        for a in adps:
            if a in cond_mappings:
                cond = cond_mappings[a]
    
    if len(nums) > 0:
        if len(vals) > 0: vals.pop(0)
        for num in nums:
            vals.append(num)
        if not col and is_int(vals[0]):
                col = 'age'
        elif not col and is_float(vals[0]):
            col = 'size'

    if cond == 'LIKE' and len(vals) > 0 and (is_int(vals[0]) or is_float(vals[0])):
        cond = '='

    print('PARSED ==> ','table name: ', tabl, 'col name: ', col,'val: ',vals,'cond: ',cond)

    if cond == 'BETWEEN':    
        whr_data = [
            {'col_name' : col, 'cond': cond, 'col_val': vals},
        ]
    else:
        if len(vals) > 0:
            whr_data = [{'col_name' : col, 'cond': cond, 'col_val': vals[0]}]
        else:
            whr_data = [{'col_name' : col, 'cond': cond, 'col_val': vals}]
    sel_data = {'table_name' : tabl, 'sel_cols':'COUNT(*)'}
    sql_q = populate_sql_template('SEL_WITH_CONDS', sel_data, whr_data)
    print('SQL QUERY==> ', sql_q, '\n')

    return sql_q

def fetch_patient_data_better(rs, args):
    raw_uq = rs.get_uservar("user_1", "raw_uq")
    print('USER QUERY==> ', raw_uq)
    # extract args
    subs, verbs, adps, nums, np = extract_args_better(raw_uq)
    try:
        sql_q = make_sql_query(subs, verbs, adps, nums, np)
        patient_count = query_db(sql_q)
    except Exception as e:
        print(e)
        resp = "Sorry, something went wrong. Please try again later."
        return resp

    if patient_count == 0:
        resp = "There are no patients like that. Is there anything else I can help you with?"
    elif patient_count == 1:
        resp = "There is " + str(patient_count) + " patient like that. Is there anything else I can help you with?"
    else:
        resp = "There are about " + str(patient_count) + " patients like that. Is there anything else I can help you with?"
    return resp

# baseline
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
  return round(100 * float(part)/float(whole), 2)

def find_size_mapping(obj):
    if is_float(obj):
        size_val = float(obj)
    elif is_int(obj):
        size_val = int(obj)
    else:
        return obj    
    if(size_val <= 5):
        return "tiny"
    elif(5 < size_val <= 8):
        return "small"
    elif(8 < size_val <= 14):
        return "medium"
    elif(14 < size_val < 22):
        return "large"
    elif(size_val >= 22):
        return "giant"
    else:
        return obj

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
        if is_int(obj):
            age_val = int(obj)
        else:
            return obj    
        if( 38 <= age_val <= 58):
            return "category generation x"
        elif(age_val <= 37):
            return "category generation y"
        elif(age_val >= 74):
            return "age category silent generation"
        elif(56 <= age_val <= 73):
            return "age category baby boomers"

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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
            size = find_size_mapping(obj)
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

max_score_rule_glo = ''
user_query_glo = ''
locations = ['middle cerebral artery', 'anterior communicating artery', 'paraclinoid']
def combined_rupture_criticality(rs, args):
    rules = ['R1','R2','R3','R11','R10','R9','R8','R7','R4','R5','R6','R12','R13','R14']
    # print('args: ', args[0])
    rup_prob_per = 0
    if args[0].lower() == 'yes':
        # Find rules matched
        doc = nlp(user_query_glo)
        for term in make_terms_list(doc):
            if term in locations and term == locations[0]:
                rup_prob_per = calc_percentage(combined_rupture_probability(','.join(sample(rules, 5)), "MCA")[0][1],1)
            elif term in locations and term == locations[1]:
                # rules_dict = make_rules_dict("ACOA_Rule_Matrix_1358.txt")
                rup_prob_per = calc_percentage(combined_rupture_probability(','.join(sample(rules, 5)), "ACOM")[0][1],1)
            elif term in locations and term == locations[2]:
                # print('pcom')
                rup_prob_per = calc_percentage(combined_rupture_probability(','.join(sample(rules, 5)), "PCOM")[0][1],1)
        
        print('raw_uq: ', user_query_glo)
        # rup_prob_per = calc_percentage(combined_rupture_probability('R1,R2', "MCA")[0][1], 1)
        # print('combined: ', combined_rupture_probability('R1,R2', "MCA")[0][1])
        resp = "The combined rupture probability for this case would be close to " + str(rup_prob_per) + "%. Is there anything else I can help you with?"
        return resp
    elif args[0].lower() == 'no':
        print(max_score_rule_glo)
        rup_prob_per = calc_percentage(max_score_rule_glo, 1)
        resp = "The rupture probability for this case would be close to " + str(rup_prob_per) + "%. Is there anything else I can help you with?"
        return resp

# V2.0
def fetch_rupture_criticality(rs, args):
    raw_uq = rs.get_uservar("user_1", "raw_uq")
    global user_query_glo 
    user_query_glo = raw_uq
    rup_prob = 0
    # stop word removal
    # replace tokens expand contractions
    # Enrichment of user query using a medical ontology
    # onto_based_enrichment(sentence)
    uq = ' '.join(raw_uq.split())
    uq = process_text(uq, nlp)

    uq_list = uq.split()
    ind = -1
    try:
        ind = uq_list.index('size')
    except:
        pass
    if ind != -1:
        uq = uq.replace(uq_list[ind+1], find_size_mapping(uq_list[ind+1]))
    ind_age = -1
    try:
        ind_age = uq_list.index('age')
    except:
        pass
    if ind_age != -1:
       uq = uq.replace(uq_list[ind_age+1], find_mapping(uq_list[ind_age+1]))

    rules_dict = make_rules_dict("assets/rupture_prediction_rules.txt")
    max_score = 0.0
    max_overlap_len = 0
    max_score_rule = ""
    max_overlap_rule = ""
    rul_score_dict = {}
    for rule in rules_dict:
        uq_set = set(args)
        rule_set = set(rule.split())
        overlap = uq_set.intersection(rule_set)
        score = calculate_similarity(uq, rule, nlp)
        rul_score_dict[rule] = score
        # print(rule, score)
        if score > max_score:
            max_score = score
            max_score_rule = rule
        # if len(overlap) > max_overlap_len:
        #     max_overlap_len = len(overlap)
        #     max_overlap_rule = rule
    global max_score_rule_glo 
    max_score_rule_glo = rules_dict[max_score_rule]
    # print(uq," | ",max_score_rule," | ",max_score," | ",rules_dict[max_score_rule])
    # print(uq," | ",max_overlap_rule," | ",max_overlap_len," | ",rules_dict[max_overlap_rule])
    
    # print(rul_score_dict)
    count = 0
    for w in sorted(rul_score_dict, key=rul_score_dict.get, reverse=True):
        if rul_score_dict[w] > 0.87:
            count = count + 1
            # print(w, rul_score_dict[w])
    print(count)
    rup_prob_per = 0
    if count == 1:
        rup_prob_per = calc_percentage(list(rul_score_dict.values())[0], 1)
        resp = "The rupture probability for this case would be close to " + str(rup_prob_per) + "%. Is there anything else I can help you with?"
        return resp
    elif count > 1:
        resp = "Multiple prediction rules matched for your query. Do you want to get a combined rupture probability?"
        return resp

    # Response
    if rup_prob == 0:
        resp = "Sorry, I could not calculate the rupture probability. Is there anything else I can help you with?"
    
    return resp

# V1.0
# def fetch_rupture_criticality(rs, args):
#     possible_subs = ['aneurysm', 'location', 'age', 'gender', 'smoking', 
#     'history', 'smoking', 'habit', 'race', 'size', 'side', 'patient']
#     possible_preds = ['is', 'greater', 'over', 'under', 'less than', 'has', 'between', 'had', 'was']
#     stop_words = ['what','how','of','a','an','the','me','tell','can','you','are','were', 
#     'ages', 'age', 'aged', 'gender', 'genders', 'race', 'disease', 'and', 'whose', 'who', 'on']
#     sub = ''
#     pre = ''
#     obj = ''
#     spo_list = []
#     if 'size' not in args or 'location' not in args: return "Size or Location of Aneurysm is missing. Please retry with the corrected query" 
#     for arg in args:
#         if arg == "and":
#             spo_list.append(SubPreObj(sub.strip(),lemmatizer(pre.strip(), u"VERB")[0],obj.strip()))
#             sub = ''
#             pre = ''
#             obj = ''
#         if arg in possible_subs:
#             sub = sub + ' ' +arg      
#         elif arg in possible_preds:
#             pre = pre + ' ' +arg
#         elif arg in stop_words:
#             continue
#         else:
#             obj = obj + ' ' + arg
    
#     if sub or pre or obj:
#         spo_list.append(SubPreObj(sub.strip(),lemmatizer(pre.strip(), u"VERB")[0],obj.strip()))

#     pprint(spo_list)
#     sql1, sql2 = map_spo_to_sql_rup(spo_list)
#     rup_prob = query_db(sql1)
#     if(rup_prob == 0):
#         rup_prob = query_db(sql2)

#     if rup_prob == 0:
#         resp = "Sorry, I could not calculate the rupture probability. Is there anything else I can help you with?"
#     else:
#         rup_prob_per = calc_percentage(rup_prob.decode(), 10)
#         resp = "The rupture probability for this case would be close to " + str(rup_prob_per) + "%. Is there anything else I can help you with?"
#     return resp

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

def fetch_rupture_criticality_convo(rs, args):
    print(args)

def query_db_rup(args_dict):
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
    # mycursor = myDB.cursor(prepared=True)
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