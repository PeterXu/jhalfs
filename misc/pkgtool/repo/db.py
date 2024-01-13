from mods.utils import EmptyObject

lfs_items = [
    {   "title":        "Installing Basic System Software", 
        "uri":          "chapter08/chapter08.html",
    },
]

blfs_items = [
    {   "title":        "Security", 
        "uri":          "postlfs/security.html",
    },
    {   "title":        "File Systems and Disk Management", 
        "uri":          "postlfs/filesystems.html",
    },
    {   "title":        "Text Editors", 
        "uri":          "postlfs/editors.html",
    },
    {   "title":        "Shells", 
        "uri":          "postlfs/shells.html",
    },
    {   "title":        "Virtualization", 
        "uri":          "postlfs/virtualization.html",
    },
    {   "title":        "General Libraries",
        "uri":          "general/genlib.html",
    },
    {   "title":        "Graphics and Font Libraries",
        "uri":          "general/graphlib.html",
    },
    {   "title":        "General Utilities",
        "uri":          "general/genutils.html",
    },
    {   "title":        "System Utilities",
        "uri":          "general/sysutils.html",
    },
    {   "title":        "Programming",
        "uri":          "general/prog.html",
    },
    {   "title":        "Connecting to a Network",
        "uri":          "basicnet/connect.html",
    },
    {   "title":        "Networking Programs",
        "uri":          "basicnet/netprogs.html",
    },
    {   "title":        "Networking Libraries",
        "uri":          "basicnet/netlibs.html",
    },
    {   "title":        "Text Web Browsers",
        "uri":          "basicnet/textweb.html",
    },
    {   "title":        "Mail/News Clients",
        "uri":          "basicnet/mailnews.html",
    },
    {   "title":        "Major Servers",
        "uri":          "server/majorservers.html",
    },
    {   "title":        "Mail Server Software",
        "uri":          "server/mail.html",
    },
    {   "title":        "Databases",
        "uri":          "server/databases.html",
    },
    {   "title":        "Other Server Software",
        "uri":          "server/other.html",
    },
    {   "title":        "",
        "uri":          "",
    },
]

def get_repo_db(kind=None):
    obj = EmptyObject()
    obj.root = "https://www.linuxfromscratch.org/lfs/view/stable/"
    if kind == "blfs":
        obj.root = "https://www.linuxfromscratch.org/blfs/view/stable/"
    obj.items = []
    items = lfs_items if kind != "blfs" else blfs_items
    for item in items:
        one = EmptyObject()
        one.setattrs(item)
        obj.items.append(one)
    return obj


