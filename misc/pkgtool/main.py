#!/usr/bin/python3
# peterxu

import os
import sys
import enum
from pathlib import Path


##=========================
## >P0: command kind/parse
##=========================

class CommandKind(enum.Enum):
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


##================================
## >P2: commands and descriptions
##================================

#>reserverd for begin-marking
def _todo_begin():
    pass

"""
Perform a substring search of cask tokens and formula names for text. If 
text is flanked by slashes, it is interpreted as a regular expression.

      --desc                       Search for formulae with a description
                                   matching text and casks with a name or
                                   description matching text.
      --fedora                     Search for text in the given database.
      --debian                     Search for text in the given database.
      --ubuntu                     Search for text in the given database.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_common
def do_search(args):
    """[options] text|/regex/ [...]"""
    pass
    return True

"""
Display brief statistics for your Homebrew installation. If a formula or
cask is provided, show summary of information about it.

      --json                       Print a JSON representation.
      --installed                  Print JSON of formulae that are currently
                                   installed.
  -v, --verbose                    Show more verbose analytics data for
                                   formula.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -h, --help                       Show this message.
"""
@df_common
def do_info(args):
    """[options] [formula|cask ...]"""
    pass
    return True

"""
Install a formula or cask. Additional options specific to a formula may be
appended to the command.

Unless HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK is set, brew upgrade or brew
reinstall will be run for outdated dependents and dependents with broken
linkage, respectively.

Unless HOMEBREW_NO_INSTALL_CLEANUP is set, brew cleanup will then be run for
the installed formulae or, every 30 days, for all formulae.

Unless HOMEBREW_NO_INSTALL_UPGRADE is set, brew install formula will
upgrade formula if it is already installed but outdated.

  -d, --debug                      If brewing fails, open an interactive
                                   debugging session with access to IRB or a
                                   shell inside the temporary build directory.
  -f, --force                      Install formulae without checking for
                                   previously installed keg-only or non-migrated
                                   versions. When installing casks, overwrite
                                   existing files (binaries and symlinks are
                                   excluded, unless originally from the same
                                   cask).
  -v, --verbose                    Print the verification and post-install
                                   steps.
  -n, --dry-run                    Show what would be installed, but do not
                                   actually install anything.
      --ignore-dependencies        An unsupported Homebrew development option to
                                   skip installing any dependencies of any kind.
                                   If the dependencies are not already present,
                                   the formula will have issues. If you're not
                                   developing Homebrew, consider adjusting your
                                   PATH rather than using this option.
      --only-dependencies          Install the dependencies with specified
                                   options but do not install the formula
                                   itself.
      --cc                         Attempt to compile using the specified
                                   compiler, which should be the name of the
                                   compiler's executable, e.g. gcc-7 for GCC
                                   7. In order to use LLVM's clang, specify
                                   llvm_clang.
  -s, --build-from-source          Compile formula from source even if a
                                   bottle is provided. Dependencies will still
                                   be installed from bottles if they are
                                   available.
      --include-test               Install testing dependencies required to run
                                   brew test formula.
      --HEAD                       If formula defines it, install the HEAD
                                   version, aka. main, trunk, unstable, master.
      --keep-tmp                   Retain the temporary files created during
                                   installation.
      --debug-symbols              Generate debug symbols on build. Source will
                                   be retained in a cache directory.
      --skip-post-install          Install but skip any post-install steps.
      --overwrite                  Delete files that already exist in the prefix
                                   while linking.
      --appdir                     Target location for Applications (default:
                                   /Applications).
      --language                   Comma-separated list of language codes to
                                   prefer for cask installation.
  -q, --quiet                      Make some output more quiet.
  -h, --help                       Show this message.
"""
@df_common
def do_install(args):
    """[options] formula|cask [...]"""
    pass
    return True

"""
Uninstall a formula or cask.

  -f, --force                      Delete all installed versions of formula.
                                   Uninstall even if cask is not installed,
                                   overwrite existing files and ignore errors
                                   when removing files.
      --zap                        Remove all files associated with a cask.
                                   May remove files which are shared between
                                   applications.
      --ignore-dependencies        Don't fail uninstall, even if formula is a
                                   dependency of any installed formulae.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_common
def do_uninstall(args):
    """[options] installed_formula|installed_cask"""
    pass
    return True

"""
Fetch the newest version of Homebrew and all formulae from GitHub using git(1)
and perform any necessary migrations.

      --merge                      Use git merge to apply updates (rather than
                                   git rebase).
      --auto-update                Run on auto-updates (e.g. before brew
                                   install). Skips some slower steps.
  -f, --force                      Always do a slower, full update check (even
                                   if unnecessary).
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Print the directories checked and git
                                   operations performed.
  -d, --debug                      Display a trace of all shell commands as they
                                   are executed.
  -h, --help                       Show this message.
"""
@df_common
def do_update(args):
    """[options]"""
    pass
    return True

"""
Upgrade outdated casks and outdated, unpinned formulae using the same options
they were originally installed with, plus any appended brew formula options. If
cask or formula are specified, upgrade only the given cask or formula
kegs (unless they are pinned; see pin, unpin).

Unless HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK is set, brew upgrade or brew
reinstall will be run for outdated dependents and dependents with broken
linkage, respectively.

Unless HOMEBREW_NO_INSTALL_CLEANUP is set, brew cleanup will then be run for
the upgraded formulae or, every 30 days, for all formulae.

  -d, --debug                      If brewing fails, open an interactive
                                   debugging session with access to IRB or a
                                   shell inside the temporary build directory.
  -f, --force                      Install formulae without checking for
                                   previously installed keg-only or non-migrated
                                   versions. When installing casks, overwrite
                                   existing files (binaries and symlinks are
                                   excluded, unless originally from the same
                                   cask).
  -v, --verbose                    Print the verification and post-install
                                   steps.
  -n, --dry-run                    Show what would be upgraded, but do not
                                   actually upgrade anything.
  -s, --build-from-source          Compile formula from source even if a
                                   bottle is available.
      --debug-symbols              Generate debug symbols on build. Source will
                                   be retained in a cache directory.
      --appdir                     Target location for Applications (default:
                                   /Applications).
      --language                   Comma-separated list of language codes to
                                   prefer for cask installation.
  -q, --quiet                      Make some output more quiet.
  -h, --help                       Show this message.
"""
@df_common
def do_upgrade(args):
    """[options] [outdated_formula|outdated_cask ...]"""
    pass
    return True

"""
List all installed formulae and casks. If formula is provided, summarise the
paths within its current keg. If cask is provided, list its artifacts.

      --versions                   Show the version number for installed
                                   formulae, or only the specified formulae if
                                   formula are provided.
  -1                               Force output to be one entry per line. This
                                   is the default when output is not to a
                                   terminal.
  -l                               List formulae and/or casks in long format.
                                   Has no effect when a formula or cask name is
                                   passed as an argument.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_common
def do_list(args):
    """[options] [installed_formula|installed_cask ...]"""
    pass
    return True

#------------------

"""
Symlink all of formula's installed files into Homebrew's prefix. This is done
automatically when you install formulae but can be useful for manual
installations.

      --overwrite                  Delete files that already exist in the prefix
                                   while linking.
  -n, --dry-run                    List files which would be linked or deleted
                                   by brew link --overwrite without actually
                                   linking or deleting any files.
  -f, --force                      Allow keg-only formulae to be linked.
      --HEAD                       Link the HEAD version of the formula if it is
                                   installed.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
def do_link(args):
    """[options] installed_formula [...]"""
    pass
    return True

"""
Remove symlinks for formula from Homebrew's prefix. This can be useful for
temporarily disabling a formula: brew unlink formula && commands &&
brew link formula

  -n, --dry-run                    List files which would be unlinked without
                                   actually unlinking or deleting any files.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
def do_unlink(args):
    """[--dry-run] installed_formula [...]"""
    pass
    return True

"""
Pin the specified formula, preventing them from being upgraded when issuing
the brew upgrade formula command. See also unpin.

Note: Other packages which depend on newer versions of a pinned formula might
not install or run correctly.

  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
def do_pin(args):
    """installed_formula [...]"""
    pass
    return True

"""
Unpin formula, allowing them to be upgraded by brew upgrade formula. See
also pin.

  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
def do_unpin(args):
    """installed_formula [...]"""
    pass

#------------------

"""
Show Homebrew and system configuration info useful for debugging. If you file a
bug report, you will be required to provide this information.

  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_trouble_shoot
def do_config(args):
    """"""
    pass
    return True

"""
Check your system for potential problems. Will exit with a non-zero status if
any potential problems are found.

Please note that these warnings are just used to help the Homebrew maintainers
with debugging if you file an issue. If everything you use Homebrew for is
working fine: please don't worry or file an issue; just ignore this.

      --list-checks                List all audit methods, which can be run
                                   individually if provided as arguments.
  -D, --audit-debug                Enable debugging and profiling of audit
                                   methods.
  -d, --debug                      Display any debugging information.
  -q, --quiet                      Make some output more quiet.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_trouble_shoot
def do_doctor(args):
    """[--list-checks] [--audit-debug] [diagnostic_check ...]"""
    pass
    return True

#------------------

"""
Show lists of built-in and external commands.

  -q, --quiet                      List only the names of commands without
                                   category headers.
      --include-aliases            Include aliases of internal commands.
  -d, --debug                      Display any debugging information.
  -v, --verbose                    Make some output more verbose.
  -h, --help                       Show this message.
"""
@df_further_help
def do_commands(args):
    """[--quiet] [--include-aliases]"""
    if args:
        return
    print("==> All commands")
    for k in _get_kind(CommandKind.ALL):
        print("  zen", k)
    print()
    return True


@df_further_help
def do_help(args):
    if args and args[0] != "help":
        cmd = _get_cmd(args[0])
        if not cmd:
            print("Error: Unknown command: ", args[0], "\n")
            return False
        print("Usage: zen", args[0], cmd.get("simple", ""), "\n")
        print(cmd.get("detail"), "\n")
        return True

    print("Example usage:")
    ckind = _get_kind(CommandKind.COMMON_USAGE)
    for k in ckind:
        print("  zen", k, ckind[k].get("simple", "").upper())
    print("\nTroubleshooting:")
    for k in _get_kind(CommandKind.TROUBLE_SHOOT):
        print("  zen", k)
    print("\nFurther help:")
    for k in _get_kind(CommandKind.FURTHER_HELP):
        print("  zen", k, {"help":"[command]"}.get(k, "").upper())
    print("  man zen")
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

def _do_generate():
    try:
        items = todo_parse_docs(__file__)
    except:
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

if __name__ == '__main__':
    _do_init()
    if len(sys.argv) < 2:
        do_help(None)
        sys.exit(0)
    if sys.argv[1] == "generate":
        _do_generate()
        sys.exit(0)
    cmd = _get_cmd(sys.argv[1])
    bret = cmd["func"](sys.argv[2:]) if cmd else None
    if bret is None: print("Error: Unknown command: ", sys.argv[1], "\n")
    iret = 0 if bret else 1
    sys.exit(iret)

