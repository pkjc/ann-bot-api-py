import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from Bioportal import get_syns
from spacy.lang.en.stop_words import STOP_WORDS

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
    nlp = spacy.load('en_core_web_md')
    sentence = nlp(sentence)
    term_list =[]
    for chunk in sentence.noun_chunks:
        filtered_txt = remove_stopwords(chunk.text)
        if not filtered_txt:
            continue
        else:
            term_list.append(filtered_txt)
    return set(term_list)

def enrich_sentence_biop(sentence):
    terms_list = make_terms_list(sentence)
    enriched_sentence = []
    for term in terms_list:
        synonyms = get_syns(term)
        enriched_sentence.append(term)
        if synonyms:
            for s in synonyms:
                enriched_sentence.append('{}'.format(s + ' '))

    # Let's see our enriched sentence
    return ' '.join(enriched_sentence)


print(enrich_sentence_biop('What is the rupture criticality of a patient whose aneurysm location is anterior communicating artery and age is 30?'))