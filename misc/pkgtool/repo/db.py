from mods.utils import EmptyObject

#document.querySelectorAll("body.lfs>div.book>div.toc>ul>li")[4]
lfs_items = [
    {   "start":        "Installing Basic System Software",
        "stop":         "System Configuration",
        "root":         "https://www.linuxfromscratch.org/lfs/view/stable/index.html",
        "tmpdir":       ".zen_tmp_lfs",
        "datadir":      ".zen_data_lfs",
    },
]

#document.querySelectorAll("body.blfs>div.book>div.toc>ul>li")[2]
blfs_items = [
    {   "start":        "Security",
        "stop":         "Creative Commons License",
        "root":         "https://www.linuxfromscratch.org/blfs/view/stable/index.html",
        "tmpdir":       ".zen_tmp_blfs",
        "datadir":      ".zen_data_blfs",
    },
]

def get_repo_db(kind):
    items = None
    if kind == "lfs":    items = lfs_items
    elif kind == "blfs": items = blfs_items
    if not items: return None
    obj = EmptyObject()
    obj.items = []
    for item in items:
        one = EmptyObject()
        one.setattrs(item)
        obj.items.append(one)
    return obj

