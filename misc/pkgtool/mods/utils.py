import os
import sys
import re
import urllib
from urllib import request, error
from pathlib import Path

#default without attr, but could add new.
class EmptyObject(object):
    def __getattr__(self, name):
        return None
    def setattr(self, name, value):
        self.__dict__[name] = value
    def setattrs(self, dt):
        for k, v in dt.items(): self.setattr(k, v)
    def items(self):
        return self.__dict__.items()
    def size(self):
        return len(self.__dict__)


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
    def update_make_oneline(cls, script, line_mark=""):
        if type(script) != type(""): return script
        parts = script.strip().split("\n")
        if len(parts) <= 1: return script
        line_mark = " " + line_mark

        lines = []
        preline = None
        for item in parts:
            curline = item.rstrip()
            if preline:
                add_sc = True
                codes = preline.split()
                if len(codes) > 0:
                    if codes[0] in ["if", "elif", "else", "case", "select", "until", "while", "for"]:
                        add_sc = False
                    if codes[0] in ["then", "in", "do"]:
                        add_sc = False
                    #fi/esac/done: should add
                if not preline.endswith("\\"):
                    if preline.endswith(";"): add_sc = False
                    elif preline.endswith(")"): add_sc = False
                    if curline.lstrip().startswith(";") and not curline.lstrip().startswith(";;"):
                        add_sc = False
                    if add_sc:
                        preline += ";"
                    preline += line_mark
                    preline += "\\"
                lines.append(preline)
            preline = curline
        lines.append(preline)
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


