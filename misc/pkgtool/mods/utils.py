import os
import sys
import urllib
from urllib import request, error
from pathlib import Path

class Logger:
    @classmethod
    def i(*args, **kwargs):
        print("[INFO]", *args, **kwargs, file=sys.stdout)

    @classmethod
    def w(*args, **kwargs):
        print("[WARN]", *args, **kwargs, file=sys.stdout)

    @classmethod
    def e(*args, **kwargs):
        print("[ERRO]", *args, **kwargs, file=sys.stderr)


class Utils:
    # fpath should be pathlib.Path
    @classmethod
    def write_lines(fpath, lines, crlf="\n"):
        count = 0
        with fpath.open("w") as fp:
            for item in lines:
                if count > 0: fp.write(crlf)
                fp.write(item)
                count += 1
        return count == len(lines)

    @classmethod
    def download_url(url, dname, fname=None):
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

