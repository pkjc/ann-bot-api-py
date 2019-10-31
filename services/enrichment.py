import spacy
from services.Bioportal import get_semantically_similar_terms
from spacy.lang.en.stop_words import STOP_WORDS
from services.txt_cleanup_utils import replace_tokens
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 

# def enrich_sentence(sentence):
#     # Load an spacy model (supported models are "es" and "en") 
#     nlp = spacy.load('en_core_web_md')
#     nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
    
#     # Imagine we want to enrich the following sentence with synonyms
#     sentence = nlp(sentence)

#     # spaCy WordNet lets you find synonyms by domain of interest
#     # for example medical
#     medical_domains = ['medicine', 'health', 'surgery', 'physiology', 'radiology','anatomy']
#     enriched_sentence = []

#     # For each token in the sentence
#     for token in sentence:
#         # print(token._.wordnet.wordnet_domains())
#         # We get those synsets within the desired domains
#         synsets = token._.wordnet.wordnet_synsets_for_domain(medical_domains)
#         if len(synsets) == 0:
#            synsets = token._.wordnet.synsets()

#         if synsets:
#             lemmas_for_synset = []
#             for s in synsets:
#                 # If we found a synset in the medical domains
#                 # we get the variants and add them to the enriched sentence
#                 lemmas_for_synset.extend(s.lemma_names())
#                 enriched_sentence.append('({})'.format('|'.join(set(lemmas_for_synset))))
#         else:
#             enriched_sentence.append(token.text)

#     # Let's see our enriched sentence
#     return ' '.join(enriched_sentence)

nlp = spacy.load('en_core_web_md')
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

def remove_stopwords(txt):
    txt = txt.lower()
    if txt in STOP_WORDS:
        return ''
    else:
        filtered = []
        for tok in txt.split():
            if tok not in STOP_WORDS:
                filtered.append(tok)
        return ' '.join(filtered)

def make_terms_list(sentence):
    term_list =[]
    for chunk in sentence.noun_chunks:
        filtered_txt = remove_stopwords(chunk.text)
        if not filtered_txt:
            continue
        else:
            if len(filtered_txt.split()) > 1:
                term_list.append(filtered_txt)
    return set(term_list)

def onto_based_enrichment(sent):
    # 2.	Run the NLP pipeline on S
    sent_nlp = nlp(sent)
    # 3.	Make a list of all the nouns and noun chunks identified in the NLP pipeline
    # 4.	Get a list of multi-word concepts - See Algorithm 2
    term_list = set()
    term_list = make_terms_list(sent_nlp)
    # 5.	For each term in the noun list:
    # for token in sent_nlp:
    #     if token.pos_ is 'NOUN' or token.pos_ is 'ADJ':
    #         term_list.add(token.lemma_)
    print(term_list)
    syno_lst = []
    for term in term_list:
        sent = sent.replace(term, ' ' + term + ' '.join(get_semantically_similar_terms(term, nlp)))
        # syno_lst.extend(get_semantically_similar_terms(term, nlp))
        # syno_lst.extend(wordnet_enrichment(term))
    term_list.update(syno_lst)
    return sent

def wordnet_enrichment(token):
    token = nlp(token)
    medical_domains = ['medicine', 'health', 'surgery', 'physiology', 'radiology','anatomy']
    synsets = token._.wordnet.wordnet_synsets_for_domain(medical_domains)
    if synsets:
        lemmas_for_synset = []
        for s in synsets:
            lemmas_for_synset.extend(s.lemma_names())
        print(token, lemmas_for_synset)

print(onto_based_enrichment("give me the rupture criticality for a patient whose aneurysm location is superaclanoid internal carotid artery and size is 3.5 and age is 40 and aneurysm is on left side"))


# def enrich_sentence_biop(sentence):
#     terms_list = make_terms_list(sentence)
#     enriched_sentence = []
#     for term in terms_list:
#         synonyms = get_syns(term)
#         enriched_sentence.append(term)
#         if synonyms:
#             for s in synonyms:
#                 enriched_sentence.append('{}'.format(s + ' '))
#     # Let's see our enriched sentence
#     return ' '.join(enriched_sentence)