import os
import sys
import time
import enum
import random
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup

from mods.utils import Logger, Utils, EmptyObject
from repo.template import mak_template
from repo.db import get_repo_db


def check_if_package(pname):
    name = pname.strip()
    pos = name.rfind("-")
    if pos > 0 and Utils.check_if_version(name[pos+1:]):
        return True
    return False

def get_temp_dpath(dname):
    dpath = Path(tempfile.gettempdir()).joinpath(dname)
    dpath.mkdir(exist_ok=True)
    return dpath

def get_data_dpath(dname):
    dpath = Path(os.path.realpath(os.curdir)).joinpath(dname)
    dpath.mkdir(exist_ok=True)
    return dpath


def todo_parse_repo(kind):
    kind = "lfs"
    db = get_repo_db(kind)
    for item in db.items:
        dname = get_temp_dpath(item.tmpdir)
        fname, ret = download_file(item.root, dname)
        if not fname: continue
        #Logger.i("read index:", item.root, fname, ret)
        results = []
        with open(fname, "rb") as f:
            results = parse_index(f.read(), item)
        datpath = get_data_dpath(item.datadir)
        for pkg in results:
            url = os.path.join(os.path.dirname(item.root), pkg[0])
            #print(url, dname, pkg[1])
            parse_package(url, dname, pkg[1], datpath)
            #break
    pass

def parse_index(html_doc, repo):
    results = []
    is_start = False
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.select("div.book>div.toc>ul>li>ul>li")
    for e in elements:
        title = e.select_one("h4")
        if not title: continue
        if title.text.strip().find(repo.start) != -1:
            is_start = True
        if not is_start: continue
        if title.text.strip().find(repo.stop) != -1:
            break
        items = e.select("li>a")
        for item in items:
            link = item.get("href", None)
            if not link or not check_if_package(item.text):
                continue
            results.append([link, item.text])
        pass
    return results

def parse_package(url, dname, pname, datpath):
    fname, ret = download_file(url, dname)
    #print(url, fname, dname, ret)
    if not fname: return False
    with open(fname, "rb") as f:
        data = parse_detail(pname, f.read())
        gen_makefile(pname, data, datpath)
    if ret == 2:
        time.sleep(random.choice([0.1, 0.3, 0.1, 0.1, 0.2]))
    return True

def download_file(url, dname, name=None):
    if not url: return None, -1
    if not os.path.exists(dname): return None, -1
    bname = name if name else os.path.basename(url)
    fname = os.path.join(dname, bname)
    if os.path.exists(fname): return fname, 1
    furl = url
    if name: furl = os.path.join(os.path.dirname(url), name)
    fname = Utils.download_url(furl, dname)
    return fname, 2

#chapter08/chapter08.html: document.querySelectorAll("div.toc>ul>li>a")
def parse_toc(html_doc):
    results = []
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.select("div.toc>ul>li>a")
    for item in elements:
        link = item.get("href")
        if not link: continue
        if not check_if_package(item.text):
            Logger.w("skip link:", link)
            continue
        bname = os.path.basename(link)
        #if bname in repo.start_uris: continue
        #if bname in repo.stop_uris: break
        #print(item, item.get("href"), item.text)
        results.append([link, item.text])
    return results

#document.querySelector("body.lfs>div>div.package")
#document.querySelector("body.blfs>div>div.package")
#document.querySelectorAll("div>div.installation>pre.userinput>kbd.command")
#document.querySelector("div>div.content")
def parse_detail(name, html_doc):
    results = {}
    soup = BeautifulSoup(html_doc, 'html.parser')
    kind = "lfs"
    if not soup.select_one("body.lfs"):
        kind = "blfs"
        if not soup.select_one("body.blfs"): return False

    # A. parse <div.package>: basic info
    data = []
    package = soup.select_one("body.%s>div>div.package" % kind)
    if not package: return False
    if kind == "lfs":
        p = package.select_one("p")
        hintro = [p.text.strip() if p else "Unknown"]
        hinfo = parse_segmentedlist_items(name, package)
        data = [hintro, hinfo, []]
    else:
        ptr = None
        hintro, hinfo, hdeps  = [""], [""], [""]
        for e in package.find_all(recursive=False):
            is_top = False
            if e.name == "h2":
                ptr = hintro
                is_top = True
            elif e.name == "p": pass
            elif e.name == "h3":
                text = e.text.rstrip()
                if text.endswith("Package Information"):
                    ptr = hinfo
                    is_top = True
                elif text.endswith("Dependencies"):
                    ptr = hdeps
                    is_top = True
            elif e.name == "div":
                for i in e.select("ul.compact>li.listitem"):
                    if ptr: ptr.append(i.text.strip())
                e = None
            elif e.name == "h4": pass
            if ptr and e:
                ptr.append(e.text.strip())
                if is_top: ptr.append("")
        data = [hintro[1:], hinfo[1:], hdeps[1:]]
    results["h_package"] = data

    # B. parse <div.installation>: build/install
    data = []
    installation = soup.select_one("body.%s>div>div.installation" % kind)
    if installation:
        last_p = None
        for e in installation.find_all(recursive=False):
            if e.name == "pre":
                cmd = e.select_one("kbd.command")
                if cmd: data.append([last_p, cmd.text.strip()])
                last_p = None
            elif e.name == "p": last_p = e.text.strip()
    results["h_install"] = data

    # C. parse <div.configuration>: post-install config
    data = []
    configuration = soup.select("body.%s>div>div.configuration" % kind)
    for config in configuration:
        lines = []
        for e in config.find_all(recursive=False):
            if e.name in ["h2", "p"]: lines.append(e.text)
            elif e.name == "pre":
                lines.append("<code>\n%s\n<code>" % e.text)
            elif e.name == "div": pass
            data.append(lines)
    results["h_config"] = data

    # D. parse <div.content>: post-install content
    data = []
    content = soup.select_one("body.%s>div>div.content" % kind)
    if content:
        items1 = parse_segmentedlist_items(name, content)
        items2 = parse_variablelist_items(name, content)
        data = [items1, items2]
        #if name.lower().startswith("acl"): print(data)
    results["h_content"] = data
    return results

def parse_segmentedlist_items(name, element):
    results = []
    segs = element.select("div.segmentedlist>div.seglistitem>div.seg")
    for item in segs:
        title = item.select_one("strong.segtitle")
        body = item.select_one("span.segbody")
        if title and body: results.append(title.text.strip() + " " + body.text.strip())
    return results

def parse_variablelist_items(name, element):
    results = []
    items = element.select("div.variablelist>table>tbody>tr")
    for item in items:
        parts = item.select("td>p")
        if not len(parts) == 2: continue
        left, right = parts[0].select_one("span"), parts[1]
        #if name.lower().startswith("acl"): print(left.text)
        if left and right: results.append([left.text.strip(), right.text.strip()])
    return results


@enum.unique
class StepInstall(enum.IntEnum):
    PREPROC     = enum.auto()
    CONFIG      = enum.auto()
    BUILD       = enum.auto()
    TEST        = enum.auto()
    INSTALL     = enum.auto()
    POSTPROC    = enum.auto()
    UNKNOWN     = enum.auto()
    END         = enum.auto()

class MakDetail(object):
    name    = ""
    version = ""
    package = {}
    scripts = {}

def gen_makefile(name, data, datpath):
    if not name or not data or not datpath:
        return False
    name = name.split()[0]

    mak = MakDetail()
    mak.name = name
    pos = name.rfind("-")
    if pos > 0 and Utils.check_if_version(name[pos+1:]):
        mak.name = name[:pos]
        mak.version = name[pos+1:]
    name = mak.name
    mak.name = mak.name.replace("::", "-")
    #print(name, mak.name, mak.version)

    package = data.get("h_package", [[], [], []])
    mak.package["intro"] = "\n".join(package[0])
    mak.package["info"] = "\n".join(package[1])
    mak.package["deps"] = "\n".join(package[2])

    rets = []
    content = data.get("h_content", [[], []])
    rets.extend(content[0])
    for item in content[1]: rets.append(": ".join(item))
    mak.package["content"] = "\n".join(rets)

    rets = {}
    line_mark = "<<newline>>"
    subdir_script = None
    install = data.get("h_install", [])
    if install:
        index = StepInstall.PREPROC
        for item in install:
            detail, script = item
            if not detail: detail = ""
            detail = Utils.replace_all_spaces(detail, "_").lower()

            have_subdir = False
            for i in [0]:
                #>config
                k = index - 1
                if detail.startswith("prepare_%s_for_compilation" % name.lower()):
                    k = StepInstall.CONFIG #gcc/glibc/xml-parser
                elif detail.find("dedicated_build_directory") != -1:
                    k = StepInstall.CONFIG #gcc/glibc
                    have_subdir = True
                elif detail.find("built_in_a_subdirectory") != -1:
                    k = StepInstall.CONFIG #e2fsprogs
                    have_subdir = True
                if k >= index: index = k; break
                have_subdir = False
                #>build
                k = index - 1
                if detail.startswith("compile_the_package"):
                    k = StepInstall.BUILD  #gcc/glibc/xml-parser
                elif detail.startswith("compile_%s" % name.lower()):
                    k = StepInstall.BUILD  #wheel/meson/markupsafe/flit-core
                elif detail.startswith("build_the_package"):
                    k = StepInstall.BUILD  #jinja2
                elif detail.startswith("build_%s" % name.lower()):
                    k = StepInstall.BUILD
                elif detail.startswith("build_and_install_the_package"):
                    k = StepInstall.BUILD #dejagnu
                if k >= index: index = k; break
                #>test
                k = index - 1
                if detail.find("_tests_") != -1 or detail.startswith("to_test_the") or detail.startswith("test_the"):
                    k = StepInstall.TEST #binutils
                if k >= index: index = k; break
                #>install
                k = index - 1
                if detail.startswith("install_the_package"):
                    index = StepInstall.INSTALL #jinja2/meson/markupsafe/flit-core/gcc/..
                elif detail.startswith("install_%s" % name.lower()):
                    index = StepInstall.INSTALL #wheel
                elif detail.startswith("to_install_the"):
                    index = StepInstall.INSTALL #make-ca
                if k >= index: index = k; break
                #>postproc
                k = index - 1
                if detail.find("the_following_command") != -1:
                    index = StepInstall.POSTPROC #make-ca
                elif detail.find("sanity_checks") != -1:
                    index = StepInstall.POSTPROC #gcc
                if k >= index: index = k; break
                #>others...
                if detail.startswith("run_the_newly_compiled"):
                    index += 1 #bash
            #if name.lower() == "xml::parser": print(item[0], index, detail)
            line = Utils.update_make_oneline(script, line_mark)
            line = Utils.update_make_var(line)
            if have_subdir: subdir_script = line
            if index >= StepInstall.END: index = StepInstall.UNKNOWN
            key = StepInstall(index)
            val = rets.get(key, [])
            val.append(line)
            rets[key] = val
        pass
    sp = "; %s\\\n" % line_mark
    for key in StepInstall:
        val = rets.get(key, [])
        lines = []
        if val and key > StepInstall.CONFIG and subdir_script:
            lines.append(subdir_script)
        lines.extend(val)
        mak.scripts[key.name.lower()] = sp.join(lines)

    # output
    mdata = mak_template.format(mak = mak)
    fpath = datpath.joinpath("Makefile.%s" % mak.name.lower())
    #print(fpath)
    fpath.write_text(mdata)
    return True

