#Import all the dependencies
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from pprint import pprint
from sklearn.metrics.pairwise import cosine_similarity
import wikipedia
import spacy
nlp = spacy.load("en_core_web_md")

# an_wiki = wikipedia.page("Aneurysm")
# # print(an_wiki.url)
# data = an_wiki.content
# data_doc = nlp(data)
# sentences = [sent.string.strip() for sent in data_doc.sents]
# print(sentences, "\n\n\n")
# dataset_list = ''.join(sentences)
# dataset_array = []
# for item in dataset_list.split(','): # comma, or other
#     dataset_array.append(item)

# print(dataset_array)
# data = ["I love machine learning. Its awesome.",
#         "I love coding in python",
#         "I love building chatbots",
#         "He loves chatbots",
#         "chatbots are liked by everyone",
#         "He likes chatbots"
#         "Chatbots are also known as chatterbots",
#         "chatterbots are same as chatbots",
#         "Conversational AI is implemented using conversational agents",
#         "they chat amagingly well"]

# tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(dataset_array)]

# max_epochs = 100
# vec_size = 20
# alpha = 0.025

# model = Doc2Vec(size=vec_size,
#                 alpha=alpha, 
#                 min_alpha=0.00025,
#                 min_count=1,
#                 dm =1)
  
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
# print("Model Saved")

model= Doc2Vec.load("d2v.model")
#to find the vector of a document which is not in training data
td1 = "give me the rupture criticality for a patient whose aneurysm location is anterior communicating artery"
td2 = "how many patients whose aneurysm ruptured are over the age of 50"

td1 = nlp(td1)
td2 = nlp(td2)

td1_ = [token for token in td1 if not token.is_stop]
td2_ = [token for token in td1 if not token.is_stop]
# tokenizer = nlp.Defaults.create_tokenizer(nlp)
# test_data1 = tokenizer(td1_)
# test_data2 = tokenizer(td2_)
# test_data1 = word_tokenize(td1_)
# test_data2 = word_tokenize(td2_)
v1 = model.infer_vector(td1_).reshape(1,-1)
v2 = model.infer_vector(td2_).reshape(1,-1)
print("V1_infer ", v1)
print("V2_infer ", v2)
print("simi ", cosine_similarity(v1, v2))

# to find most similar doc using tags
# similar_doc = model.docvecs.most_similar('I love chatbots'.lower())
# print("Most sim: ", similar_doc)

# to find vector of doc in training data using tags or in other words, printing the vector of document at index 1 in training data
# print(model.docvecs['1'])