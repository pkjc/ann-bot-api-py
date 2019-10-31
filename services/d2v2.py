# from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
# from services.Doc2VecHelper import Doc2VecHelper
from services.SpacySimilarity import calculate_similarity

# stop_words = set(stopwords.words('english')) 

# d2v_helper = Doc2VecHelper("ml_models/d2v.ltd.wikipedia.model")

# user_queries = [
#     """give me the rupture probability for a patient whose aneurysm is located at anterior communicating artery and size is tiny and gender is male and patient has motor deficits""",
#     """give me the rupture criticality for a patient whose aneurysm location is Superaclanoid Internal Carotid Artery and size is 3.5 and race is african american and age is 40""",
#     """give me the rupture criticality for a patient whose aneurysm location is Paraclinoid and size is large and race is asian and patient is a smoker""",
#     """give me the rupture criticality for a patient whose aneurysm location is MCA and size is medium and patient has hypertension and patient has multiple aneurysms """,
#     """give me the rupture criticality for a patient whose aneurysm location is superaclanoid internal carotid artery and size is small and age is 60 and aneurysm is on left side""",
#     ]

def make_rules_dict(rules_file_path):
    rules_dict = {}
    if not rules_file_path:
        rules_file_path = 'assets/rupture_prediction_rules.txt'
    with open(rules_file_path) as fp:
        for i, line in enumerate(fp):
            rules_dict[line.split('\t')[0]] = line.split('\t')[1].strip()
    return rules_dict

# def calc_sim_runner():
#     rules_dict = make_rules_dict("")
#     for uq in user_queries:
#         max_score = 0.0
#         max_score_rule = ""
#         for rule in rules_dict:
#             # score = d2v_helper.calc_sentence_similarity(uq, rule)
#             score = calculate_similarity(uq, rule)
#             # print(rule.strip(),",",str(score).strip())
#             if score > max_score:
#                 max_score = score
#                 max_score_rule = rule
#         print(uq,",",max_score_rule,",",max_score,",",rules_dict[max_score_rule])

# calc_sim_runner()

# d2v_helper.calc_sentence_similarity("What is a cerebral aneurysm?", "An aneurysm is a weak area in a blood vessel that usually enlarges.")

# d2v_helper.calc_sentence_similarity(
#     "location anterior communicating artery size tiny gender female motor deficits",
#     "give me the rupture criticality for a patient whose aneurysm location is anterior communicating artery and size is tiny and gender is female and patient has motor deficits")

