import os
import sys
import time
import random
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup

from mods.utils import Logger, Utils
from repo.template import mak_template


DEFAULT_URL = "https://www.linuxfromscratch.org/lfs/view/stable/chapter08/chapter08.html"
BEGIN_HTMLS = ["introduction.html", "pkgmgt.html"]
END_HTMLS = ["aboutdebug.html", "stripping.html", "cleanup.html"]

def get_temp_dpath():
    dpath = Path(tempfile.gettempdir()).joinpath(".zen_repo_0")
    dpath.mkdir(exist_ok=True)
    return dpath

def get_make_fpath(name):
    dpath = Path(os.path.realpath(os.curdir)).joinpath("repo/.data")
    dpath.mkdir(exist_ok=True)
    fpath = dpath.joinpath("Makefile.%s" % name.lower())
    return fpath


def todo_parse_repo(url):
    if not url: url = DEFAULT_URL.strip()
    fname, _ = download_file(url)
    if not fname: return False
    with open(fname) as f1:
        results = parse_toc(f1.read())
        for item in results:
            sname, ret = download_file(url, item[0])
            if not sname: continue
            with open(sname) as f2:
                ret = parse_detail(f2.read())
                gen_makefile(item[1], ret)
            if ret == 2:
                time.sleep(random.choice([0.1, 0.3, 0.1]))
            #break
    return True

def download_file(url, name=None):
    if not url: return None, -1
    dname = get_temp_dpath()
    bname = name if name else os.path.basename(url)
    fname = os.path.join(dname, bname)
    if os.path.exists(fname): return fname, 1
    furl = url
    if name: furl = os.path.join(os.path.dirname(url), name)
    fname = Utils.download_url(furl, dname)
    return fname, 2

#document.querySelectorAll("div.toc>ul>li>a")
def parse_toc(html_doc):
    results = []
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.select("div.toc>ul>li>a")
    for item in elements:
        link = item.get("href")
        if not link: continue
        bname = os.path.basename(link)
        if bname in BEGIN_HTMLS: continue
        if bname in END_HTMLS: break
        #print(item, item.get("href"), item.text)
        results.append([link, item.text])
    return results

#document.querySelector("div.wrap>div.package")
#document.querySelectorAll("div.wrap>div.installation>pre.userinput>kbd.command")
#document.querySelector("div.wrap>div.content")
def parse_detail(html_doc):
    results = [None, None, None]
    soup = BeautifulSoup(html_doc, 'html.parser')
    package = soup.select_one("div.wrap>div.package")
    if package:
        p = package.select_one("p")
        desc = p.text.strip() if p else None
        more = parse_segmentedlist_items(package)
        #print(desc, more)
        results[0] = [desc, more]

    installation = soup.select_one("div.wrap>div.installation")
    if installation:
        steps = []
        last_p = None
        elements = installation.find_all(recursive=False)
        for item in elements:
            if item.name == "pre":
                cmd = item.select_one("kbd.command")
                if cmd: steps.append([last_p, cmd.text.strip()])
                last_p = None
            elif item.name == "p": last_p = item.text.strip()
        #print (len(steps), steps)
        results[1] = steps

    content = soup.select_one("div.wrap>div.content")
    if content:
        more = parse_segmentedlist_items(content)
        items = parse_variablelist_items(content)
        #print(more, items)
        results[2] = [more, items]
    return results

def parse_segmentedlist_items(element):
    results = []
    segs = element.select("div.segmentedlist>div.seglistitem>div.seg")
    for item in segs:
        title = item.select_one("strong.segtitle")
        body = item.select_one("span.segbody")
        if title and body: results.append(title.text.strip() + " " + body.text.strip())
    return results

def parse_variablelist_items(element):
    results = []
    items = element.select("div.variablelist>table>tbody>tr")
    for item in items:
        parts = item.select("td>p")
        if not len(parts) == 2: continue
        left, right = parts[0].select_one("span>code"), parts[1]
        if left and right: results.append([left.text.strip(), right.text.strip()])
    return results


class Package(object):
    name    = ""
    version = ""
    desc    = ""
    st_prepare  = ""
    st_config   = ""
    st_build    = ""
    st_test     = ""
    st_install  = ""
    st_unknown  = ""

def gen_makefile(name, info):
    if not info or len(info) != 3: return
    pkg = Package()
    pkg.name = name
    pos = name.rfind("-")
    if pos > 0 and Utils.check_if_version(name[pos+1:]):
        pkg.name = name[:pos]
        pkg.version = name[pos+1:]
        #print(pkg.name, pkg.version)

    desc = []
    if info[0]:
        desc = [info[0][0], ""]
        desc.extend(info[0][1])
    if info[2]:
        more, items = info[2]
        desc.extend(more)
        for item in items: desc.append(": ".join(item))
    pkg.desc = "\n".join(desc)

    if info[1]:
        data = {}
        index = 0
        states = ["prepare", "config", "build", "test", "install", "unknown"]
        for item in info[1]:
            detail = item[0]
            if not detail: detail = ""
            detail = detail.replace("\n", "")
            detail = detail.replace("\t", "")
            detail = detail.replace(" ", "")
            if item[1].startswith("./configure") or item[1].startswith("../configure"):
                index = 1
            elif index <= 1 and detail.find("dedicatedbuilddirectory") > 0:
                index = 1
            elif item[1].startswith("make"):
                if item[1].find(" install") > 0: index = 4
                elif item[1].find(" check") > 0 or item[1].find(" test") > 0: index = 3
                else: index += 1
            line = Utils.update_make_oneline(item[1])
            line = Utils.update_make_var(line)
            #if pkg.name.lower() == "glibc": print(">>>", item)
            if index >= len(states): index = len(states) - 1
            key = states[index]
            val = data.get(key, [])
            val.append(line)
            data[key] = val
        sp = "; \\\n"
        #data["prepare"] = ["echo 123", "ls /tmp/", "echo 456", "ls /tmp/2"]
        pkg.st_prepare =   sp.join(data.get("prepare", []))
        pkg.st_config =    sp.join(data.get("config", []))
        pkg.st_build =     sp.join(data.get("build", []))
        pkg.st_test =      sp.join(data.get("test", []))
        pkg.st_install =   sp.join(data.get("install", []))
        pkg.st_unknown =   sp.join(data.get("unknown", []))

    val = mak_template.format(pkg = pkg)
    fpath = get_make_fpath(pkg.name)
    fpath.write_text(val)
    pass

