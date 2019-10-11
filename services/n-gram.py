# import spacy
# nlp = spacy.load('en_core_web_md')
# doc = nlp("how many patients are 30 years old")

# for noun_phrase in list(doc.noun_chunks):
#     noun_phrase.merge(noun_phrase.root.tag_, noun_phrase.root.lemma_, noun_phrase.root.ent_type_)

# for token in doc:
#     print(token.text,token.pos_) 

from nltk import bigrams, trigrams
from nltk import word_tokenize
from nltk.corpus import stopwords
import nltk

stoplist = set(stopwords.words('english'))
tokenized_sent = word_tokenize("How many patients are african american?")

# tokenized_sent_nostop = [token for token in tokenized_sent if token not in stoplist]

nouns = []
for word,pos in nltk.pos_tag(tokenized_sent):
    # print(word, pos)
    if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'
            or pos == 'JJ' or pos == 'VB' or pos == 'VBP' or pos == 'VBG'):
        nouns.append(word)

print(list(bigrams(nouns)))
print(list(trigrams(nouns)))
