import os
import sys
import time
import enum
import random
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup

from mods.utils import Log, Utils, EmptyObject
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
    Log.i('Try to update repo:', kind)
    #kind = "blfs"
    db = get_repo_db(kind)
    if not db: return None
    for item in db.items:
        dname = get_temp_dpath(item.tmpdir)
        fname, ret = download_file(item.root, dname)
        if not fname: continue
        Log.i("To read one %s-index:" % kind, item.root)
        results = []
        with open(fname, "rb") as f:
            results = parse_index(f.read(), item)
        Log.i("The package number of current index:", len(results))
        datpath = get_data_dpath(item.datadir)
        for pkg in results:
            url = os.path.join(os.path.dirname(item.root), pkg[0])
            #print(kind, url, dname, pkg[1])
            parse_package(kind, url, dname, pkg[1], datpath)
    Log.i('End to update repo:', kind)
    return True

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

def parse_package(kind, url, dname, pname, datpath):
    fname, ret = download_file(url, dname)
    #print(url, fname, dname, ret)
    if not fname: return False
    with open(fname, "rb") as f:
        data = parse_detail(kind, pname, f.read())
        gen_makefile(kind, pname, data, datpath)
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
            Log.w("skip link:", link)
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
def parse_detail(kind, name, html_doc):
    results = {}
    soup = BeautifulSoup(html_doc, 'html.parser')

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
        def parse_kbd_command(one):
            last_p = None
            for e in one.find_all(recursive=False):
                if e.name == "pre":
                    cmd = e.select_one("kbd.command")
                    if cmd: data.append([last_p, cmd.text.strip()])
                    last_p = None
                elif e.name == "p": last_p = e.text.strip()
        parse_kbd_command(installation)
        if not data:
            for one in installation.select("div.sect3"):
                parse_kbd_command(one)
    if not data:
        Log.w("No installation for", name)
        return False
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
    if not data:
        #Log.w("No configuration for", name)
        pass
    results["h_config"] = data

    # C.1 parse <div.commands>
    data = []
    commands = soup.select("body.%s>div>div.commands" % kind)
    for cmd in commands:
        lines = []
        for e in cmd.find_all(recursive=False):
            if e.name in ["h2", "p"]: lines.append(e.text)
        data.append(lines)
    if not data:
        #Log.w("No commands for", name)
        pass
    results["h_command"] = data

    # D. parse <div.content>: post-install content
    data = []
    content = soup.select_one("body.%s>div>div.content" % kind)
    if content:
        items1 = parse_segmentedlist_items(name, content)
        items2 = parse_variablelist_items(name, content)
        data = [items1, items2]
        #if name.lower().startswith("acl"): print(data)
    if not data:
        Log.w("No content for", name)
        #return False
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

def parse_lfs_install(name, detail, script, index):
    if not detail: detail = ""
    detail = Utils.replace_all_spaces(detail, "_").lower()
    sh_subdir = []
    for i in [0]:
        ##>config
        k = index - 1
        if detail.startswith("prepare_%s_for_compilation" % name.lower()):
            k = StepInstall.CONFIG #gcc/glibc/xml-parser
        elif detail.find("dedicated_build_directory") != -1:
            k = StepInstall.CONFIG #gcc/glibc
            sh_subdir = [k, "mkdir -p build && cd build"]
        elif detail.find("built_in_a_subdirectory") != -1:
            k = StepInstall.CONFIG #e2fsprogs
            sh_subdir = [k, "mkdir -p build && cd build"]
        if k >= index: index = k; break
        sh_subdir = []
        ##>build
        k = index - 1
        if detail.startswith("compile_the_package"):
            k = StepInstall.BUILD  #gcc/glibc/xml-parser
        elif detail.startswith("compile_%s" % name.lower()):
            k = StepInstall.BUILD  #wheel/meson/markupsafe/flit-core
        elif detail.startswith("build_the_package"):
            k = StepInstall.BUILD  #jinja2
        elif detail.startswith("build_%s" % name.lower()):
            k = StepInstall.BUILD
        if k >= index: index = k; break
        ##>test
        k = index - 1
        if detail.find("_tests_") != -1 or detail.startswith("to_test_the") or detail.startswith("test_the"):
            k = StepInstall.TEST #binutils
        if k >= index: index = k; break
        ##>install
        k = index - 1
        if detail.startswith("install_the_package"):
            k = StepInstall.INSTALL #jinja2/meson/markupsafe/flit-core/gcc/..
        elif detail.startswith("install_%s" % name.lower()):
            k = StepInstall.INSTALL #wheel
        elif detail.startswith("build_and_install_the_package"):
            k = StepInstall.INSTALL #dejagnu
        if k >= index: index = k; break
        ##>postproc
        k = index - 1
        if detail.find("sanity_checks") != -1:
            k = StepInstall.POSTPROC #gcc
        if k >= index: index = k; break
        ##>others...
        if detail.startswith("run_the_newly_compiled"):
            index += 1 #bash
    return index, sh_subdir

def parse_blfs_install(name, detail, script, index):
    if not detail: detail = ""
    detail = Utils.replace_all_spaces(detail, "_").lower()
    script = Utils.replace_all_spaces(script, "_").lower()
    sh_subdir = []
    for i in [0]:
        ##>config
        k = index - 1
        if k >= index: index = k; break
        ##>build
        k = index - 1
        if detail.find("install_%s_by_running" % name.lower()) != -1:
            k = StepInstall.BUILD
            if script.find("mkdir_build") != -1 or script.find("mkdir_-v_build") != -1:
                if script.find("cd_build") != -1:
                    sh_subdir = [k, "mkdir -p build && cd build"]
        if k >= index: index = k; break
        sh_subdir = []
        ##>test
        k = index - 1
        if detail.find("_tests_") != -1 or detail.startswith("to_test_the") or detail.startswith("test_the"):
            k = StepInstall.TEST #binutils
        if k >= index: index = k; break
        ##>install
        k = index - 1
        if detail.startswith("now,_as_the_root_user"):
            k = StepInstall.INSTALL
        elif script.startswith("make_install"):
            k = StepInstall.INSTALL
        if k >= index: index = k; break
        ##>postproc
        k = index - 1
        if detail.find("the_following_command") != -1 and index == StepInstall.INSTALL:
            k = StepInstall.POSTPROC
        if k >= index: index = k; break
        ##>others...
    return index, sh_subdir

def gen_makefile(kind, name, data, datpath):
    if not kind or not name or not data or not datpath:
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
    if package:
        mak.package["intro"] = "\n".join(package[0])
        mak.package["info"] = "\n".join(package[1])
        mak.package["deps"] = "\n".join(package[2])

    rets = []
    content = data.get("h_content", [[], []])
    if content:
        rets.extend(content[0])
        for item in content[1]: rets.append(": ".join(item))
    mak.package["content"] = "\n".join(rets)

    rets = {}
    line_mark = "<<newline>>"
    subdir_script = None
    subdir_index = StepInstall.PREPROC
    install = data.get("h_install", [])
    if install:
        index = StepInstall.PREPROC
        #print(name, len(install))
        for item in install:
            detail, script = item
            fn_parse = parse_lfs_install if kind == "lfs" else parse_blfs_install
            index, sh_subdir = fn_parse(name, detail, script, index)
            #if name.lower() == "xml::parser": print(item[0], index, detail)
            line = Utils.update_make_oneline(script, line_mark)
            line = Utils.update_make_var(line)
            if sh_subdir: subdir_index, subdir_script = sh_subdir
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
        if val and key > subdir_index and subdir_script:
            lines.append(subdir_script)
        lines.extend(val)
        mak.scripts[key.name.lower()] = sp.join(lines)

    # output
    mdata = mak_template.format(mak = mak)
    fpath = datpath.joinpath("Makefile.%s" % mak.name.lower())
    #print(fpath)
    fpath.write_text(mdata)
    return True

