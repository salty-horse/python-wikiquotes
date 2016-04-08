WORD_BLACKLIST = ['quoted', 'Variant:', 'Retrieved', 'Notes:']
MIN_QUOTE_LEN = 6
MIN_QUOTE_WORDS = 3
MAIN_PAGE = "Main Page"


def is_quote(txt):
    txt_split = txt.split()
    invalid_conditions = [
        not txt or not txt[0].isupper() or len(txt) < MIN_QUOTE_LEN,
        len(txt_split) < MIN_QUOTE_WORDS,
        any(True for word in txt_split if word in WORD_BLACKLIST),
        any(word.endswith((')', ':', ']')) for word in txt_split),
    ]

    # Returns false if any invalid conditions are true, otherwise returns True.
    return not any(invalid_conditions)


def extract_quotes(tree, max_quotes):
    quotes_list = []

    # Remove table of contents
    toc_list = tree.xpath('//div[@id="toc"]')
    for toc in toc_list:
        toc.getparent().remove(toc)

    # List items inside unordered lists
    node_list = tree.xpath('//div/ul/li|//h2')

    # Description tags inside description lists,
    # first one is generally not a quote
    dd_list = tree.xpath('//div/dl/dd')[1:]
    if len(dd_list) > len(node_list):
        node_list += dd_list

    skip_to_next_heading = False
    for node in node_list:
        if node.tag != 'h2' and skip_to_next_heading:
            continue

        if node.tag == 'h2':
            skip_to_next_heading = False
            heading_text = node.text_content().lower()

            # Commence skipping
            if heading_text in ('cast', 'see also', 'external links'):
                skip_to_next_heading = True

            continue

        # Handle li/dd

        uls = node.xpath('ul')
        for ul in uls:
            ul.getparent().remove(ul)

        txt = node.text_content().strip()
        if is_quote(txt) and max_quotes > len(quotes_list):
            txt_normal = ' '.join(txt.split())
            quotes_list.append(txt_normal)

            if max_quotes == len(quotes_list):
                break

    return quotes_list


def qotd(html_tree):
    tree = html_tree.get_element_by_id('mf-qotd')

    raw_quote = tree.xpath('div/div/table/tr')[0].text_content().split('~')
    quote = raw_quote[0].strip()
    author = raw_quote[1].strip()
    return quote, author
