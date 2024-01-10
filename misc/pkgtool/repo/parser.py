import os
import sys
import time
import urllib
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup

from mods.utils import Logger, Utils
from repo.template import mak_template


IS_TESTING = True
DEFAULT_URL = "https://www.linuxfromscratch.org/lfs/view/stable/chapter08/chapter08.html"
DEFAULT_PATH = "repo"

def todo_parse_repo(url):
    fname = download_file(url)
    if not fname: return False
    with open(fname) as f1:
        results = parse_toc(f1.read())
        for item in results:
            sname = download_file(url, item[0])
            if not sname: continue
            with open(sname) as f2:
                ret = parse_detail(f2.read())
                gen_makefile(item[1], ret)
            break
    return True

def download_file(url, name=None):
    if IS_TESTING and not url: url = DEFAULT_URL.strip()
    if not url: return None
    dname = os.path.join(tempfile.gettempdir(), ".zen_repo_0")
    os.makedirs(dname, exist_ok=True)

    bname = name if name else os.path.basename(url)
    fname = os.path.join(dname, bname)
    if not os.path.exists(fname):
        furl = url
        if name: furl = os.path.join(os.path.dirname(url), name)
        fname = Utils.download_url(furl, dname)
    return fname

#document.querySelectorAll("div.toc>ul>li>a")
def parse_toc(html_doc):
    results = []
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.select("div.toc>ul>li>a")
    for item in elements:
        link = item.get("href")
        if not link: continue
        if link.endswith("introduction.html") or link.endswith("pkgmgt.html"):
            continue
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
        #print(left, right)
        if left and right: results.append([left.text.strip(), right.text.strip()])
    return results

def gen_makefile(name, info):
    if not info or len(info) != 3: return
    data = {
        "desc": [],
        "prepare": [],
        "config": [],
        "build": [],
        "test": [],
        "install": [],
    }
    if info[0]:
        desc = [info[0][0]]
        desc.extend(info[0][1])
        data["desc"] = desc
    if info[1]:
        for item in info[1]:
            key = "prepare"
            if item[1].startswith("./configure") or item[1].startswith("../configure"):
                key = "config"
            elif item[1].startswith("make"):
                key = "build"
                if item[1].find(" install") > 0: key = "install"
                elif item[1].find(" check") > 0 or item[1].find(" test") > 0: key = "test"
            data[key].append(item[1])
    path = Path(os.path.realpath(os.curdir)).joinpath(DEFAULT_PATH)
    fpath = path.joinpath("Makefile")
    print(path, name)
    #print(info)
    print(data)
    desc = "\n".join(data["desc"])
    config = "\n".join(data["config"])
    build = "\n".join(data["build"])
    test = "\n".join(data["test"])
    install = "\n".join(data["install"])
    val = mak_template.format(name=name, version="", desc=desc, config=config, build=build, test=test, install=install)
    fpath.write_text(val)
    pass
