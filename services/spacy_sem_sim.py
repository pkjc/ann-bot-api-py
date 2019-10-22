import spacy
from collections import Counter
from spacy_wordnet.wordnet_annotator import WordnetAnnotator 
from pprint import pprint

nlp = spacy.load('en_core_web_md')
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

sentence = nlp('give me the rupture criticality for a patient whose aneurysm location is superaclanoid internal carotid artery and size is 3.5 and age is 40 and aneurysm is on left side')

all_doms = []
for token in sentence:
    if not token.is_stop and not token.is_punct:
        doms = token._.wordnet.wordnet_domains()
        if doms:
            all_doms.extend(doms)

domain_freq = dict(Counter(all_doms))

common_domains = set()
for key in domain_freq:
    max_val = max(domain_freq.values())
    if domain_freq[key] == max_val or domain_freq[key] == max_val-1:
        common_domains.add(key)
        print(key, domain_freq[key])
# pprint(common_domains)

enriched_sentence = []
# For each token in the sentence
for token in sentence:
    # We get those synsets within the desired domains
    synsets = token._.wordnet.wordnet_synsets_for_domain(common_domains)
    if synsets:
        lemmas_for_synset = []
        for s in synsets:
            # If we found a synset in the economy domains
            # we get the variants and add them to the enriched sentence
            lemmas_for_synset.extend(s.lemma_names())
            enriched_sentence.append('({})'.format('|'.join(set(lemmas_for_synset))))
    else:
        enriched_sentence.append(token.text)

# Let's see our enriched sentence
print(' '.join(enriched_sentence))
# >> I (need|want|require) to (draw|withdraw|draw_off|take_out) 5,000 euros