import os
import sys
import re
import urllib
from urllib import request, error
from pathlib import Path

class Logger:
    @classmethod
    def i(cls, *args, **kwargs):
        print("[INFO]", *args, **kwargs, file=sys.stdout)

    @classmethod
    def w(cls, *args, **kwargs):
        print("[WARN]", *args, **kwargs, file=sys.stdout)

    @classmethod
    def e(cls, *args, **kwargs):
        print("[ERRO]", *args, **kwargs, file=sys.stderr)


class Utils:
    @classmethod
    def replace_all_spaces(cls, val, pat=""):
        if type(val) != type(""): return val
        new = re.sub(r"\s+", pat, val)
        return new

    @classmethod
    def replace_all_nonwords(cls, val, pat=""):
        if type(val) != type(""): return val
        # Remove all non-word characters (except numbers and letters)
        new = re.sub(r"[^\w\s]", '', val)
        # Replace with pat
        new = re.sub(r"\s+", pat, new)
        return new

    @classmethod
    def check_if_version(cls, val):
        if type(val) != type(""): return False
        if len(val) == 0: return False
        parts = val.strip().split(".")
        if len(parts) > 5: return False
        for item in parts:
            if not item.isdigit(): return False
        return True

    @classmethod
    def update_make_var(cls, script):
        if type(script) != type(""): return script
        return script.replace("$", "$$")

    @classmethod
    def update_make_oneline(cls, script):
        if type(script) != type(""): return script
        parts = script.strip().split("\n")
        if len(parts) <= 1: return script

        lines = []
        endpos = len(parts) - 1
        for item in parts[:endpos]:
            add_comma = True
            line = item.rstrip()
            codes = line.split()
            if len(codes) > 0:
                if codes[0] in ["if", "elif", "else", "case", "select", "until", "while", "for"]:
                    add_comma = False
                if codes[0] in ["then", "in", "do"]:
                    add_comma = False
            if not line.endswith("\\"):
                if add_comma and not line.endswith(";"): line += ";"
                line += " \\";
            lines.append(line)
        lines.append(parts[endpos])
        #print(len(parts), len(lines))
        return "\n".join(lines)

    # fpath should be pathlib.Path
    @classmethod
    def write_lines(cls, fpath, lines, crlf="\n"):
        count = 0
        with fpath.open("w") as fp:
            for item in lines:
                if count > 0: fp.write(crlf)
                fp.write(item)
                count += 1
        return count == len(lines)

    @classmethod
    def download_url(cls, url, dname, fname=None):
        dname = os.path.expanduser(dname)
        if not os.path.exists(dname):
            Logger.w("Output directory not exist: <%s>!" % dname)
            return False
        if not fname: fname = os.path.basename(url)
        fpath = os.path.join(dname, fname)
        if os.path.exists(fpath):
            Logger.w("Output filename is exist: <%s>!" % fpath)
            return False
        try:
            urllib.request.urlretrieve(url, fpath)
            return fpath
        except (urllib.error.URLError, IOError) as e:
            Logger.e("Download failed with error: ", e)
        except Exception as ex:
            Logger.w("Download failed with exception: ", ex)
        return False

