from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords 
import wikipedia
from html2txt import html2txt
from Doc2VecHelper import Doc2VecHelper
from SpacySimilarity import calculate_similarity
from wiki_utils import get_related_wiki_pages

# stop_words = set(stopwords.words('english')) 

# wiki_pages = [
#     "Intracranial aneurysm", "Aneurysm", "Diabetes", 
#     "Obesity", "Artery", "Thrombosis", "Aortic aneurysm",
#     "Hypertension", "Tobacco smoking", "Vasa vasorum", "Blood vessel", 
#     "Circulatory system", "Myocardial infarction", "ventricular aneurysms", "venous",
#     "coronary artery aneurysms", "brain", "capillary aneurysms", "Loss of balance", 
#     "alcoholism", "obesity", "hypertension", "tobacco use", "infectious intracranial aneurysms", 
#     "anterior communicating artery", "autosomal dominant polycystic kidney disease", "Surgical clipping",
#     "pseudoaneurysm", "venous", "nervous system", "cerebral cortex"
# ]

# data = ""
# for wp in wiki_pages:
#     an_wiki = wikipedia.page(wp)
#     data += an_wiki.content

# with open('corpus.txt', 'r') as file:
#     data += file.read().replace('\n', '')

# # with open("corpus.txt", 'r', encoding="utf8", errors='ignore') as f:
# #   data = f.read()

# data = sent_tokenize(data)

# clean_data = []
# for s in data:
#     word_tokens = word_tokenize(s)
#     clean_toks = [w for w in word_tokens if not w in stop_words]
#     cleaned_sen = ' '.join(clean_toks)
#     clean_data.append(cleaned_sen.strip())

# tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(clean_data)]

# max_epochs = 100
# vec_size = 20
# alpha = 0.025

# model = Doc2Vec(vector_size=vec_size,
#                 alpha=alpha, 
#                 min_alpha=0.025,
#                 min_count=1,
#                 dm =0)

# model.build_vocab(tagged_data)

# for epoch in range(max_epochs):
#     print('iteration {0}'.format(epoch))
#     model.train(tagged_data,
#                 total_examples=model.corpus_count,
#                 epochs=model.iter)
#     # decrease the learning rate
#     model.alpha -= 0.0002
#     # fix the learning rate, no decay
#     model.min_alpha = model.alpha

# model.save("d2v.model")
# print("Model Saved!")

# model = Doc2Vec.load("modeldow.doc2vec")

# word_tokens = word_tokenize("what is an Aneurysm?".lower()) 
# test_data = [w for w in word_tokens if not w in stop_words and w.isalpha()] 
# v1 = model.infer_vector(test_data)

# word_tokens1 = word_tokenize("Smoking is a major cause of Aneurysm.".lower()) 
# test_data1 = [w for w in word_tokens1 if not w in stop_words and w.isalpha()] 
# v2 = model.infer_vector(test_data1)

# # print("V1_infer", v1)
# # print("V2_infer", v2)

# score = model.wv.n_similarity(test_data, test_data1)

# print("score ", score)

# similar_doc = model.docvecs.most_similar(positive=[model.infer_vector(test_data)],topn=5)

# for i in range(0,len(similar_doc)):
#     print("\n", tagged_data[int(similar_doc[i][0])], similar_doc[i][1])

# wiki_pages = get_related_wiki_pages("Aneurysm")

# d2v_helper = Doc2VecHelper(None, "wiki", wiki_pages)

d2v_helper = Doc2VecHelper("ml_models/d2v.ltd.wikipedia.model")

user_queries = [
    """give me the rupture probability for a patient whose aneurysm is located at anterior communicating artery and size is tiny and gender is male and patient has motor deficits""",
    """give me the rupture criticality for a patient whose aneurysm location is Superaclanoid Internal Carotid Artery and size is 3.5 and race is african american and age is 40""",
    """give me the rupture criticality for a patient whose aneurysm location is Paraclinoid and size is large and race is asian and patient is a smoker""",
    """give me the rupture criticality for a patient whose aneurysm location is MCA and size is medium and patient has hypertension and patient has multiple aneurysms """,
    """give me the rupture criticality for a patient whose aneurysm location is superaclanoid internal carotid artery and size is small and age is 60 and aneurysm is on left side""",
    ]

def make_rules_dict(rules_file_path):
    rules_dict = {}
    if not rules_file_path:
        rules_file_path = 'rupture_prediction_rules.txt'
    with open(rules_file_path) as fp:
        for i, line in enumerate(fp):
            rules_dict[line.split('\t')[0]] = line.split('\t')[1].strip()
    # print(rules_dict)
    return rules_dict

def calc_sim_runner():
    rules_dict = make_rules_dict("")
    # print("rule,score")
    for uq in user_queries:
        max_score = 0.0
        max_score_rule = ""
        for rule in rules_dict:
            score = d2v_helper.calc_sentence_similarity(uq, rule)
            # score = calculate_similarity(uq, rule)
            # print(rule.strip(),",",str(score).strip())
            if score > max_score:
                max_score = score
                max_score_rule = rule
        print(uq,",",max_score_rule,",",max_score,",",rules_dict[max_score_rule])

calc_sim_runner()

# d2v_helper.calc_sentence_similarity("What is a cerebral aneurysm?", "An aneurysm is a weak area in a blood vessel that usually enlarges.")

# d2v_helper.calc_sentence_similarity(
#     "location anterior communicating artery size tiny gender female motor deficits",
#     "give me the rupture criticality for a patient whose aneurysm location is anterior communicating artery and size is tiny and gender is female and patient has motor deficits")

