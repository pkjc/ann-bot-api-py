# from gensim.models.doc2vec import Doc2Vec, TaggedDocument
# from nltk.tokenize import word_tokenize, sent_tokenize
# from nltk.corpus import stopwords 
# import wikipedia

# class Doc2VecHelper:
#     stop_words = set(stopwords.words('english'))
#     model = None
#     # extract text content from wikipedia pages
#     def fetch_wikipages_content(self, wiki_pages):
#         wikipages_content = ""
#         for wiki_page in wiki_pages:
#             an_wiki = wikipedia.page(wiki_page)
#             wikipages_content += an_wiki.content
#         return wikipages_content

#     # makes text lowercase and removes stop words and punctuation
#     def clean_text(self, txt):
#         word_tokens = word_tokenize(txt.lower())
#         clean_toks = [w for w in word_tokens if not w in Doc2VecHelper.stop_words and w.isalpha()]
#         return clean_toks

#     # trains and saved model using passed str
#     def make_trained_model(self, training_data_src):
#         cleaned_training_data = []
#         if(training_data_src == 'wiki'):
#             wikipages_content = sent_tokenize(self.fetch_wikipages_content(self.wiki_pages))
#             for sent in wikipages_content:
#                 cleaned_text = ' '.join(self.clean_text(sent)).strip()
#                 cleaned_training_data.append(cleaned_text)
#         tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(cleaned_training_data)]
#         model = self.train_model(tagged_data)
#         model.save("ml_models/d2v.ltd.wikipedia.model")
#         return model
    
#     # trains model with the tagged_data and parameters passed to it
#     def train_model(self, tagged_data, max_epochs = 100, vec_size = 20, alpha = 0.025):
#         model = Doc2Vec(vector_size=vec_size,
#                         alpha=alpha, 
#                         min_alpha=0.025,
#                         min_count=2,
#                         dm=1)
#         model.build_vocab(tagged_data)
#         for epoch in range(max_epochs):
#             # print('iteration {0}'.format(epoch))
#             model.train(tagged_data,
#                         total_examples=model.corpus_count,
#                         epochs=model.iter)
#             # decrease the learning rate
#             model.alpha -= 0.0002
#             # fix the learning rate, no decay
#             model.min_alpha = model.alpha
#         return model

#     # calculates cosine sentence similarity
#     def calc_sentence_similarity(self, sent1, sent2):
#         # print(self.clean_text(sent1))
#         # print(self.clean_text(sent2))
#         v1 = Doc2VecHelper.model.infer_vector(self.clean_text(sent1))
#         v2 = Doc2VecHelper.model.infer_vector(self.clean_text(sent2))
#         # score1 = Doc2VecHelper.model.wv.n_similarity(self.clean_text(sent1), self.clean_text(sent2))
#         # print("score1 ", score1)
#         score = Doc2VecHelper.model.docvecs.similarity_unseen_docs(Doc2VecHelper.model, self.clean_text(sent1), self.clean_text(sent2))
#         # print("score ", score)
#         return score
    
#     # Initializer / Instance Attributes
#     def __init__(self, model_path=None, training_data_src=None, wiki_pages=None):
#         if model_path is None:
#             if training_data_src is not None and wiki_pages is not None:
#                 self.wiki_pages = wiki_pages
#                 Doc2VecHelper.model = self.make_trained_model('wiki')
#         else:
#             Doc2VecHelper.model = Doc2Vec.load(model_path) 