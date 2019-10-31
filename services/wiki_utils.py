import wikipedia

wikipedia.set_lang('en')

def fetch_wikipages_content(wiki_pages):
    wikipages_content = ""
    for wiki_page in wiki_pages:
        an_wiki = wikipedia.page(wiki_page)
        wikipages_content += an_wiki.content
    return wikipages_content

def get_related_wiki_pages(seed_page):
    wiki_pages = []
    seed_wiki_page = wikipedia.page(seed_page)
    for wpl in seed_wiki_page.links:
        try:
            wpl_content = wikipedia.page(wpl)
            wiki_pages.append(wpl_content.title)
        except wikipedia.exceptions.DisambiguationError as e:
            continue
        except wikipedia.exceptions.PageError as e:
            continue
    return wiki_pages

# wp_for_training = []
# wp_for_training.extend(get_related_wiki_pages("Aneurysm"))



