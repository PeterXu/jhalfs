#!/usr/bin/python3

import os
import sys
import time
from bs4 import BeautifulSoup

url_packages = "https://www.linuxfromscratch.org/lfs/view/stable/chapter03/packages.html"
url_patches = "https://www.linuxfromscratch.org/lfs/view/stable/chapter03/patches.html"

LFS = os.environ.get("LFS")
if not LFS or not os.path.exists(LFS):
    print(">ERROR: no LFS env")
    sys.exit(-1)


def parse_softs(html_doc, exts):
    results = []
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.select("dd")
    for item in elements:
        links = item.select("p>a.ulink")
        codes = item.select("p>code.literal")
        if len(links) >= 1 and len(codes) == 1:
            plink, pcode = links[0], codes[0]
            if len(links) >= 2: plink = links[1]
            ret = [plink.get("href"), pcode.text]
            results.append(ret)
        else:
            print(">SKIP: ", item)
    return results

def down_softs(soft_links):
    for item in soft_links:
        url, md5val = item[0], item[1]
        bname = os.path.basename(url)
        fdst = os.path.join(LFS, "sources", bname)
        parts = []
        parts.append('fname="%s"; fsum="%s"' % (fdst, md5val))
        parts.append('[ -f "$fname" ] && sum=$(md5sum "$fname" | cut -c 1-32)')
        parts.append('[ "$sum" = "$fsum" ] && echo "OK:   $fname exists!" && exit 0')
        parts.append('[ -f "$fname" ] && echo "SKIP: $fname broken"')
        parts.append('rm -f "$fname"')
        parts.append('echo "INFO: downing %s ..."' % url)
        parts.append('wget "%s" -O "$fname"' % url)
        cmdline = ";".join(parts)
        try: os.system(cmdline)
        except: pass
        time.sleep(0.1)

def parse_url(url, name, exts):
    fdst = "/tmp/%s" % name
    #os.system("rm -f %s" % fdst)
    if not os.path.exists(fdst):
        os.system("wget %s -O %s" % (url, fdst))
    with open(fdst) as fp:
        softs = parse_softs(fp.read(), exts)
        print(">INFO:", name, len(softs))
        down_softs(softs)
        print(">===================\n")


parse_url(url_packages, "lfs_packages.html", [".gz", ".xz"])
parse_url(url_patches, "lfs_patches.html", [".patch"])

