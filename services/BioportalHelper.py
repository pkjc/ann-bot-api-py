import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint
import re
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 

REST_URL = "http://data.bioontology.org"
API_KEY = "7d7c9925-d25c-4674-b468-f250252c7343"

nlp = spacy.load('en_core_web_md')
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

def get_json(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

# Get list of search terms
# path = os.path.join(os.path.dirname(__file__), 'classes_search_terms.txt')
# terms_file = open(path, "r")
# terms = ["blood", "aneursym", "male", "age", "gender"]
# # for line in terms_file:
# #     terms.append(line)

# # Do a search for every term
# search_results = []
# for term in terms:
#     search_results.append(get_json(REST_URL + "/search?q=" + term + "&require_exact_match=true")["collection"])

# # pprint(search_results[0][0].keys())

# # Print the results
# syn_list = set()
# for result in search_results:
#     # pprint(type(result))
#     for syn in result:
#         # pprint(syn.keys())
#         if("synonym" in syn):
#             # if(syn["matchType"] == "synonym"):
#                 # pprint(syn["prefLabel"])
#                 lowered_list = [x.lower() for x in syn["synonym"]]
#                 syn_list.update(lowered_list)

# pprint(syn_list)
def clean_up(txt):
    if re.search("([^\x00-\x7F])+", txt):
        return ''
    else: 
        txt = txt.lower()
    return txt

def get_syns(term):
    sentence = nlp(term)
    results = get_json(REST_URL + "/search?q=" + term + "&require_exact_match=true")["collection"]
    syn_list = []
    for res in results:
        pprint(res["matchType"])
        if(res["matchType"] == "synonym"):
            # semanticType
            # matchtype
            # filter by language. found at top
            if type(res["synonym"]) is list:
                lowered_list = [clean_up(x) for x in res["synonym"]]
                syn_list.extend(lowered_list)
            else:
                syn_list.extend(res["synonym"].lower())
                for token in sentence:
                    synsets = token._.wordnet.synsets()
                    for syn in synsets:
                        pprint("sim: ", syn.wup_similarity(res["synonym"].lower()))
    return set(syn_list)

pprint(get_syns("gender"))