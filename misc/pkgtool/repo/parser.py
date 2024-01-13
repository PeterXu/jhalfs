import os
import sys
import time
import enum
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


# basic system softs
def todo_parse_repo(url):
    if not url: url = DEFAULT_URL.strip()
    fname, _ = download_file(url)
    if not fname: return False
    with open(fname) as f1:
        results = parse_toc(f1.read())
        for item in results:
            sname, ret = download_file(url, item[0])
            if not sname: continue
            name = item[1]
            with open(sname) as f2:
                data = parse_detail(name, f2.read())
                gen_makefile(name, data)
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
        data = [p.text.strip() if p else "Unknown", ""]
        items = parse_segmentedlist_items(name, package)
        data.extend(items)
    else:
        ptr = None
        hintro, hinfo, hdeps  = [], [], []
        for e in package.select("*"):
            if e.name == "h2": ptr = hintro
            elif e.name == "p": pass
            elif e.name == "h3":
                text = e.text.rstrip()
                if text.endswith("Package Information"): ptr = hinfo
                elif text.endswith("Dependencie"): ptr = hdeps
            elif e.name == "div":
                for i in e.select("ul.compact>li.listitem"):
                    if ptr: ptr.append(i.text)
                e = None
            elif e.name == "h4": pass
            if ptr and e: ptr.append(e.text)
        data.extend(hintro)
        data.extend(hinfo)
        data.extend(hdeps)
    results["h_info"] = data

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

class Package(object):
    name    = ""
    version = ""
    desc    = ""
    scripts = {}

def gen_makefile(name, data):
    if not name or not data:
        return False
    name = name.split()[0]

    pkg = Package()
    pkg.name = name
    pos = name.rfind("-")
    if pos > 0 and Utils.check_if_version(name[pos+1:]):
        pkg.name = name[:pos]
        pkg.version = name[pos+1:]
    name = pkg.name
    pkg.name = pkg.name.replace("::", "-")
    #print(name, pkg.name, pkg.version)

    info = data.get("h_info", [])
    content = data.get("h_content", [])
    if content:
        info.append("")
        info.extend(content[0])
        for item in content[1]: info.append(": ".join(item))
    pkg.desc = "\n".join(info)

    install = data.get("h_install", [])
    if install:
        rets = {}
        index = StepInstall.PREPROC
        subdir_script = None
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
                if k >= index: index = k; break
                #>postproc
                k = index - 1
                if detail.find("sanity_checks") != -1:
                    index = StepInstall.POSTPROC #gcc
                if k >= index: index = k; break
                #>others...
                if detail.startswith("run_the_newly_compiled"):
                    index += 1 #bash
            #if name.lower() == "xml::parser": print(item[0], index, detail)
            line = Utils.update_make_oneline(script)
            line = Utils.update_make_var(line)
            if have_subdir: subdir_script = line
            if index >= StepInstall.END: index = StepInstall.UNKNOWN
            key = StepInstall(index)
            val = rets.get(key, [])
            val.append(line)
            rets[key] = val
        sp = "; \\\n"
        for key in StepInstall:
            val = rets.get(key, [])
            lines = []
            if val and key > StepInstall.CONFIG and subdir_script:
                lines.append(subdir_script)
            lines.extend(val)
            pkg.scripts[key.name.lower()] = sp.join(lines)
        pass

    mdata = mak_template.format(pkg = pkg)
    fpath = get_make_fpath(pkg.name)
    fpath.write_text(mdata)
    return True

