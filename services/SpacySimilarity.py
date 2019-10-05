import spacy

nlp = spacy.load("en_core_web_md")

#assign the default stopwords list to a variable

# STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS

def process_text(text):
    doc = nlp(text.lower())
    result = []
    for token in doc:
        if token.text in nlp.Defaults.stop_words:
            continue
        if token.is_punct:
            continue
        if token.lemma_ == '-PRON-':
            continue
        result.append(token.lemma_)
    return " ".join(result)

def calculate_similarity(text1, text2):
    # for chunk in nlp(text1).noun_chunks:
    #     print(chunk.text, chunk.label_, chunk.root.text)
    # for chunk in nlp(text2).noun_chunks:
    #     print(chunk.text, chunk.label_, chunk.root.text)
    p_text1 = process_text(text1)
    p_text2 = process_text(text2)
    # print("text1 without stop_words:\t", p_text1)
    # print("text2 without stop_words:\t", p_text2)
    base = nlp(p_text1)
    compare = nlp(p_text2)
    return base.similarity(compare)

# print(calculate_similarity("how many patients are african american?", "how many patients are asian?"))
# print("Similarity score:\t", calculate_similarity("how many patients are african american?", "what is the time in the captical of Japan right now?"))