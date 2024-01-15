#!/usr/bin/python3
# peterxu

import os
import sys
import enum
import argparse
from pathlib import Path
from mods.utils import Log


##=========================
## >P0: command kind/parse
##=========================

PROG = "zen"

@enum.unique
class CommandKind(enum.IntEnum):
    ALL             = 1,
    COMMON_USAGE    = 21,
    TROUBLE_SHOOT   = 22,
    FURTHER_HELP    = 23,
    END             = 100,
_ALL_COMMANDS = {
    CommandKind.ALL: {},
}
def _get_cmd(key, default=None):
    return _ALL_COMMANDS[CommandKind.ALL].get(key, default)
def _get_kind(kind, default={}):
    return _ALL_COMMANDS.get(kind, default)
def _get_kind_cmd(kind, cmd, default=None):
    return _ALL_COMMANDS.get(kind, {}).get(cmd, default)
def _add_kind_cmd(kind, cmd):
    if not kind or not cmd: return
    cret = _ALL_COMMANDS[CommandKind.ALL].get(cmd, {"MARK": 1})
    _ALL_COMMANDS[CommandKind.ALL][cmd] = cret
    if kind == CommandKind.ALL: return
    kret = _ALL_COMMANDS.get(kind, {})
    _ALL_COMMANDS[kind] = kret
    kret[cmd] = cret
def _add_cmd_prop(cmd, key, val):
    if not cmd or not key or not val: return
    cret = _ALL_COMMANDS[CommandKind.ALL].get(cmd, None)
    if cret: cret[key] = val

# name format: <do_xxxx>
def _parse_cmd(name):
    if not name: return None
    parts = name.strip().split("_")
    if len(parts) >= 2 and parts[0] == "do":
        return parts[1]
    return None
def _get_prog(name):
    cmd = _parse_cmd(name)
    if not cmd: cmd = "unknown"
    return "{0} {1}".format(PROG, cmd)


##=========================
## >P1: decorate functions
##=========================

def df_decorate(func, kind):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    cmd = _parse_cmd(func.__name__)
    _add_kind_cmd(kind, cmd)
    _add_cmd_prop(cmd, "func", func)
    return wrapper
def df_common(func):
    return df_decorate(func, CommandKind.COMMON_USAGE)
def df_trouble_shoot(func):
    return df_decorate(func, CommandKind.TROUBLE_SHOOT)
def df_further_help(func):
    return df_decorate(func, CommandKind.FURTHER_HELP)

def df_command(func):
    return df_decorate(func, CommandKind.ALL)

##================================
## >P2: commands and descriptions
##================================

def _create_argparser(fn_name, fn_desc):
    parser = argparse.ArgumentParser(prog=_get_prog(fn_name), description=fn_desc)
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='''Make some output more quiet.''')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='''Make some output more verbose.''')
    return parser

#>reserverd for begin-marking
def _todo_begin():
    pass

@df_common
def do_search(self, args):
    """[options] text|/regex/ [...]"""
    desc = '''
        Perform a substring search of cask tokens and formula names for text. If 
        text is flanked by slashes, it is interpreted as a regular expression.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--desc', action='store_true',
                        help='''Search for formulae with a description
                                matching text and casks with a name or
                                description matching text.''')
    parser.add_argument('--fedora', action='store_true',
                        help='''Search for text in the given database.''')
    parser.add_argument('--debian', action='store_true',
                        help='''Search for text in the given database.''')
    parser.add_argument('--ubuntu', action='store_true',
                        help='''Search for text in the given database.''')
    parser.add_argument('text', nargs=1,
                        help='''Search for text or regex.''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_info(self, args):
    """[options] [formula|cask ...]"""
    desc = '''
        Display brief statistics for your Homebrew installation. If a formula or
        cask is provided, show summary of information about it.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--json', action='store_true',
                        help='''Print a JSON representation.''')
    parser.add_argument('--installed', action='store_true',
                        help='''Print JSON of formulae that are currently
                                installed.''')
    parser.add_argument('package', nargs=1,
                        help='''The formula or cask''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_install(self, args):
    """[options] formula|cask [...]"""
    desc = '''
        Install a formula or cask. Additional options specific to a formula may be
        appended to the command.

        Unless HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK is set, brew upgrade or brew
        reinstall will be run for outdated dependents and dependents with broken
        linkage, respectively.

        Unless HOMEBREW_NO_INSTALL_CLEANUP is set, brew cleanup will then be run for
        the installed formulae or, every 30 days, for all formulae.

        Unless HOMEBREW_NO_INSTALL_UPGRADE is set, brew install formula will
        upgrade formula if it is already installed but outdated.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('-f', '--force', action='store_true',
                        help='''Install formulae without checking for
                                previously installed keg-only or non-migrated
                                versions. When installing casks, overwrite
                                existing files (binaries and symlinks are
                                excluded, unless originally from the same
                                cask).''')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='''Show what would be installed, but do not
                                actually install anything.''')
    parser.add_argument('--ignore-dependencies', action='store_true',
                        help='''An unsupported Homebrew development option to
                                skip installing any dependencies of any kind.''')
    parser.add_argument('--only-dependencies', action='store_true',
                        help='''Install the dependencies with specified
                                options but do not install the formula
                                itself.''')
    parser.add_argument('--cc',
                        help='''Attempt to compile using the specified
                                compiler, which should be the name of the
                                compiler's executable.''')
    parser.add_argument('-s', '--build-from-source', action='store_true',
                        help='''Compile formula from source even if a
                                bottle is provided. Dependencies will still
                                be installed from bottles if they are
                                available.''')
    parser.add_argument('--include-test', action='store_true',
                        help='''Install testing dependencies required to run
                                test formula.''')
    parser.add_argument('--HEAD', action='store_true',
                        help='''If formula defines it, install the HEAD
                                version, aka. main, trunk, unstable, master.''')
    parser.add_argument('--keep-tmp', action='store_true',
                        help='''Retain the temporary files created during
                                installation.''')
    parser.add_argument('--debug-symbols', action='store_true',
                        help='''Generate debug symbols on build. Source will
                                be retained in a cache directory.''')
    parser.add_argument('--skip-post-install', action='store_true',
                        help='''Install but skip any post-install steps.''')
    parser.add_argument('--overwrite', action='store_true',
                        help='''Delete files that already exist in the prefix
                                while linking.''')
    parser.add_argument('--appdir',
                        help='''Target location for Applications (default:
                                /Applications).''')
    parser.add_argument('--language',
                        help='''Comma-separated list of language codes to
                                prefer for cask installation.''')
    parser.add_argument('package', nargs='+',
                        help='''The formula or cask''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_uninstall(self, args):
    """[options] installed_formula|installed_cask [...]"""
    desc = '''
        Uninstall a formula or cask.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('-f', '--force', action='store_true',
                        help='''Delete all installed versions of formula.
                                Uninstall even if cask is not installed,
                                overwrite existing files and ignore errors
                                when removing files.''')
    parser.add_argument('--ignore-dependencies', action='store_true',
                        help='''Don't fail uninstall, even if formula is a
                                dependency of any installed formulae.''')
    parser.add_argument('package', nargs='+',
                        help='''The installed formula or cask''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_update(self, args):
    """[options]"""
    desc = '''
        Fetch the newest version of Homebrew and all formulae from GitHub using git(1)
        and perform any necessary migrations.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--merge', action='store_true',
                        help='''Use git merge to apply updates (rather than
                                git rebase).''')
    parser.add_argument('--auto-update', action='store_true',
                        help='''Run on auto-updates (e.g. before brew
                                install). Skips some slower steps.''')
    parser.add_argument('-f', '--force', action='store_true',
                        help='''Always do a slower, full update check (even
                                if unnecessary).''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_upgrade(self, args):
    """[options] [outdated_formula|outdated_cask ...]"""
    desc = '''
        Upgrade outdated casks and outdated, unpinned formulae using the same options
        they were originally installed with, plus any appended brew formula options. If
        cask or formula are specified, upgrade only the given cask or formula
        kegs (unless they are pinned; see pin, unpin).

        Unless HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK is set, brew upgrade or brew
        reinstall will be run for outdated dependents and dependents with broken
        linkage, respectively.

        Unless HOMEBREW_NO_INSTALL_CLEANUP is set, brew cleanup will then be run for
        the upgraded formulae or, every 30 days, for all formulae.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('-f', '--force', action='store_true',
                        help='''Install formulae without checking for
                                previously installed keg-only or non-migrated
                                versions. When installing casks, overwrite
                                existing files (binaries and symlinks are
                                excluded, unless originally from the same cask''')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='''Show what would be upgraded, but do not
                                actually upgrade anything.''')
    parser.add_argument('--debug-symbols', action='store_true',
                        help='''Generate debug symbols on build. Source will
                                be retained in a cache directory.''')
    parser.add_argument('--appdir',
                        help='''Target location for Applications (default:
                                /Applications).''')
    parser.add_argument('--language',
                        help='''Comma-separated list of language codes to
                                prefer for cask installation.''')
    parser.add_argument('package', nargs='+',
                        help='''The outdated formula or cask''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_common
def do_list(self, args):
    """[options] [installed_formula|installed_cask ...]"""
    desc = '''
        List all installed formulae and casks. If formula is provided, summarise the
        paths within its current keg. If cask is provided, list its artifacts.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--versions', action='store_true',
                        help='''Show the version number for installed
                                formulae, or only the specified formulae if
                                formula are provided.''')
    parser.add_argument('-1', dest='one', action='store_true',
                        help='''Force output to be one entry per line. This
                                is the default when output is not to a
                                terminal.''')
    parser.add_argument('-l', dest='long', action='store_true',
                        help='''List formulae and/or casks in long format.
                                Has no effect when a formula or cask name is
                                passed as an argument.''')
    parser.add_argument('package', nargs='*',
                        help='''The installed formula or cask''')
    rets = parser.parse_args(args)
    print(rets)
    return True

#------------------

@df_command
def do_link(self, args):
    """[options] installed_formula [...]"""
    desc = '''
        Symlink all of formula's installed files into Homebrew's prefix. This is done
        automatically when you install formulae but can be useful for manual
        installations.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--overwrite', action='store_true',
                        help='''Delete files that already exist in the prefix
                                while linking.''')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='''List files which would be unlinked without
                                actually unlinking or deleting any files.''')
    parser.add_argument('-f', '--force', action='store_true',
                        help='''Allow keg-only formulae to be linked.''')
    parser.add_argument('--HEAD', action='store_true',
                        help='''Link the HEAD version of the formula if it is
                                installed.''')
    parser.add_argument('package', nargs='+',
                        help='''The installed formula''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_command
def do_unlink(self, args):
    """[--dry-run] installed_formula [...]"""
    desc = '''
        Remove symlinks for formula from Homebrew's prefix. This can be useful for
        temporarily disabling a formula: brew unlink formula && commands &&
        brew link formula
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='''List files which would be unlinked without
                                actually unlinking or deleting any files.''')
    parser.add_argument('package', nargs='+',
                        help='''The installed formula''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_command
def do_pin(self, args):
    """installed_formula [...]"""
    desc = '''
        Pin the specified formula, preventing them from being upgraded when issuing
        the brew upgrade formula command. See also unpin.

        Note: Other packages which depend on newer versions of a pinned formula might
        not install or run correctly.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('package', nargs='+',
                        help='''The installed formula''')
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_command
def do_unpin(self, args):
    """installed_formula [...]"""
    desc = '''
        Unpin formula, allowing them to be upgraded by brew upgrade formula. See
        also pin.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('package', nargs='+',
                        help='''The installed formula''')
    rets = parser.parse_args(args)
    print(rets)
    pass

#------------------

@df_trouble_shoot
def do_config(self, args):
    """"""
    desc = '''
        Show Homebrew and system configuration info useful for debugging. If you file a
        bug report, you will be required to provide this information.
        '''
    parser = _create_argparser(self.__name__, desc)
    rets = parser.parse_args(args)
    print(rets)
    return True

@df_trouble_shoot
def do_doctor(self, args):
    """[--list-checks] [--audit-debug] [diagnostic_check ...]"""
    desc = '''
        Check your system for potential problems. Will exit with a non-zero status if
        any potential problems are found.

        Please note that these warnings are just used to help the Homebrew maintainers
        with debugging if you file an issue. If everything you use Homebrew for is
        working fine: please don't worry or file an issue; just ignore this.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--list-checks',
                        help='''List all audit methods, which can be run
                                individually if provided as arguments.''')
    rets = parser.parse_args(args)
    print(rets)
    return True

#------------------

@df_further_help
def do_commands(self, args):
    """[--quiet] [--include-aliases]"""
    desc = '''
        Show lists of built-in and external commands.
        '''
    parser = _create_argparser(self.__name__, desc)
    parser.add_argument('--include-aliases',
                        help='''Include aliases of internal commands.''')
    rets = parser.parse_args(args)
    print(rets)
    if args:
        return
    print("==> All commands")
    for k in _get_kind(CommandKind.ALL):
        print(" ", PROG, k)
    print()
    return True


@df_further_help
def do_help(self, args):
    if args and args[0] != "help":
        cmd = _get_cmd(args[0])
        if not cmd:
            print("Error: Unknown command: ", args[0], "\n")
            return False
        func = cmd["func"]
        func(func, ["-h"])
        return True

    print("Example usage:")
    ckind = _get_kind(CommandKind.COMMON_USAGE)
    for k in ckind:
        print(" ", PROG, k, ckind[k].get("simple", "").upper())
    print("\nTroubleshooting:")
    for k in _get_kind(CommandKind.TROUBLE_SHOOT):
        print(" ", PROG, k)
    print("\nFurther help:")
    for k in _get_kind(CommandKind.FURTHER_HELP):
        print(" ", PROG, k, {"help":"[command]"}.get(k, "").upper())
    print("  man", PROG)
    for k in _get_kind(CommandKind.END):
        pass
    print()
    return True

#>reserverd for end-marking
def _todo_end():
    pass


##======================
## >PP: loading/initing
##======================

import mods.system_config as syscfg
from docs.parser import todo_parse_docs
from repo.parser import todo_parse_repo
try:
    from docs.generated import ALL_DOCS
except:
    ALL_DOCS = []

def _do_init():
    try:
        items = todo_parse_docs(__file__)
    except:
        items = ALL_DOCS
    for item in items:
        name, key, doc = item
        _add_cmd_prop(_parse_cmd(name), key, doc)
    pass

def _do_gen_docs(args):
    try:
        items = todo_parse_docs(__file__)
    except:
        Log.w("gen-docs exception happens!")
        items = []
    ppath = Path("docs/generated.py")
    with ppath.open("w") as fp:
        fp.write('ALL_DOCS = [\n')
        for item in items:
            fp.write('  [\n')
            fp.write('    "%s",\n' % item[0])
            fp.write('    "%s",\n' % item[1])
            fp.write('    """%s"""\n' % item[2])
            fp.write('  ],\n')
        fp.write(']')
    pass

def _do_gen_repo(args):
    parser = _create_argparser('do_gen-repo', 'Generate repository.')
    parser.add_argument('site', nargs=1, choices=['lfs', 'blfs'],
                        help='''supported sites''')
    rets = parser.parse_args(args)
    todo_parse_repo(rets.site)


if __name__ == '__main__':
    _do_init()
    if len(sys.argv) < 2:
        do_help(None, None)
        sys.exit(0)
    if sys.argv[1].startswith("gen-"):
        if sys.argv[1] == "gen-docs":
            _do_gen_docs(sys.argv[2:])
        elif sys.argv[1] == "gen-repo":
            _do_gen_repo(sys.argv[2:])
        sys.exit(0)
    cmd = _get_cmd(sys.argv[1])
    func = cmd["func"] if cmd else None
    bret = func(func, sys.argv[2:]) if func else None
    if bret is None: print("Error: Unknown command: ", sys.argv[1], "\n")
    iret = 0 if bret else 1
    sys.exit(iret)

