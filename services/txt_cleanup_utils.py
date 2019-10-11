def replace_tokens(txt):
    replace_dict = {
        "&": " and ",
        "%": " percent ",
        ">": " greater-than ",
        "<": " less-than ",
        "=": " equals ",
        "#": " ",
        "~": " ",
        "/": " ",
        "\\": " ",
        "|": " ",
        "$": "",
        # Remove empty :
        " : ": " ",
        # Remove double dashes
        "--": " ",
        # Remove possesive splits
        " 's ": " ",
        # Remove quotes
        "'": "",
        '"': "",
    }
    for key, val in replace_dict.items():
            txt = txt.replace(key, val)

    # Remove blank tokens, but keep line breaks
    doc = [
        " ".join([token for token in line.split()])
        for line in txt.split("\n")
    ]

    # Remove blank lines
    doc = "\n".join(filter(None, doc))

    return doc