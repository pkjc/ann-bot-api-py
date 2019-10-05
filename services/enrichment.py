import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 

def enriched_sentence(sentence):
    # Load an spacy model (supported models are "es" and "en") 
    nlp = spacy.load('en_core_web_md')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
    
    # Imagine we want to enrich the following sentence with synonyms
    sentence = nlp(sentence)

    # spaCy WordNet lets you find synonyms by domain of interest
    # for example medical
    medical_domains = ['medicine', 'health', 'surgery', 'physiology', 'radiology','anatomy']
    enriched_sentence = []

    # For each token in the sentence
    for token in sentence:
        # print(token._.wordnet.wordnet_domains())
        # We get those synsets within the desired domains
        synsets = token._.wordnet.wordnet_synsets_for_domain(medical_domains)
        if len(synsets) == 0:
           synsets = token._.wordnet.synsets()

        if synsets:
            lemmas_for_synset = []
            for s in synsets:
                print(s.path_similarity(s))
                # If we found a synset in the medical domains
                # we get the variants and add them to the enriched sentence
                lemmas_for_synset.extend(s.lemma_names())
                enriched_sentence.append('({})'.format('|'.join(set(lemmas_for_synset))))
        else:
            enriched_sentence.append(token.text)

    # Let's see our enriched sentence
    return ' '.join(enriched_sentence)


print(enriched_sentence('rupture criticality patient aneurysm location anterior communicating artery'))