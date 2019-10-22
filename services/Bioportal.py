import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint
import re
from txt_cleanup_utils import replace_tokens
import spacy

REST_URL = "http://data.bioontology.org"
API_KEY = "7d7c9925-d25c-4674-b468-f250252c7343"
nlp = spacy.load('en_core_web_md')

def get_json(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

def clean_up(txt, term_doc):
    if re.search("([^\x00-\x7F])+", txt):
        return ''
    else: 
        txt = txt.lower()
        # Create list of word tokens after removing stopwords
        # filtered_sentence =[] 
        # for word in txt.split(' '):
        #     lexeme = nlp.vocab[word]
        #     if lexeme.is_stop == False:
        #         filtered_sentence.append(word) 
        # doc = nlp(''.join(filtered_sentence))
        txt_doc = nlp(txt)
        sim_score = txt_doc.similarity(term_doc)
        # print('txt: ', txt, sim_score)
        if sim_score == 1.0 or sim_score < 0.8:
            return ''
        txt_list = []
        for token in txt_doc:
            if token.text not in nlp.vocab:
                return ''
            else:
                if '\'' not in token.text:
                    txt_list.append(token.lemma_)

    return ' '.join([x for x in txt_list if x.isalpha()])

def get_syns(term):
    print(term)
    term_doc = nlp(term)
    results = get_json(REST_URL + "/search?q=" + term.replace(' ', '+') + "&require_exact_match=true&ontology=SNOMEDCT&also_search_properties=true")["collection"]
    results1 = get_json(REST_URL + "/search?q=" + "old".replace(' ', '+') + "&require_exact_match=true&ontology=SNOMEDCT&also_search_properties=true")["collection"]
    print("results ", len(results))
    print("results1 ", len(results))
    sem_types1 = set()
    sem_types2 = set()
    syn_list = []
    for res in results:
        # pprint(res)
        if "semanticType" in res:
            sem_types1.update(res["semanticType"])
                
    for res in results1:
        if "synonym" in res:
            pprint(res["synonym"])    
        if "semanticType" in res:
            sem_types2.update(res["semanticType"])
        # if "synonym" in res:
        #     syn = res["synonym"]
        #     if type(syn) is list:
        #         for syn_word in syn:
        #             if syn_word != term:
        #                 syn_list.append(clean_up(syn_word, term_doc))
        #     else:
        #         if syn != term:
        #             syn_list.append(clean_up(syn, term_doc))
    syno_set = set(filter(None, syn_list))

    # print("sem_types1 ", sem_types1)
    # print("sem_types2 ", sem_types2)
    intersec = sem_types1.intersection(sem_types2)
    print("intersection  ", intersec)
   
    for res in results:
        if "semanticType" in res and any(x in max(intersec,res["semanticType"],key=len) for x in min(intersec,res["semanticType"],key=len)) and "synonym" in res:
            print(res["prefLabel"])

    for res in results1:
        if "semanticType" in res and  any(x in max(intersec,res["semanticType"],key=len) for x in min(intersec,res["semanticType"],key=len)) and "synonym" in res:
            print(res["prefLabel"])

    return syno_set

get_syns("age")
# get_syns("gender")

def calculate_semantic_sim_sent(sent1, sent2):
    # tokenize both sentences
    # strip stop words
    pass