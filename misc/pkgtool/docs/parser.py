import tokenize

def todo_parse_docs(fname):
    def _extract_name(token):
        if token.type != tokenize.NAME or token.string != 'def' or token.start[1] != 0: return None
        parts = token.line.split()
        return parts[1].split("(")[0].strip() if len(parts) >= 2 else None
    def _extract_doc(text):
        key, data = '"""', text.strip()
        if not data.startswith(key): return None
        pp = data[len(key):]
        return pp[:len(pp)-len(key)].strip()

    # parse cmd docs
    docs = []
    with tokenize.open(fname) as f:
        is_begin = False
        for token in tokenize.generate_tokens(f.readline):
            name = _extract_name(token)
            if name:
                if name.startswith("_todo_begin"): is_begin = True
                elif name.startswith("_todo_end"): break
                elif name.startswith("do_"): docs.append(["def", name, token])
            elif is_begin:
                doc = _extract_doc(token.string)
                if doc: docs.append(["doc", doc, token])
        pass

    # collect docs
    cmd_docs = []
    last_item = None
    for item in docs:
        if last_item:
            name, doc, key = None, None, None
            if item[0] == "doc" and last_item[0] == "def" and item[2].start[1] > 0:
                if last_item[2].start[0] + 1 == item[2].start[0]:
                    name, doc, key = last_item[1], item[1], "simple"
            if key: cmd_docs.append([name, key, doc])
        last_item = item
    return cmd_docs

