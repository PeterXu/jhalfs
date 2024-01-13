clock_help = """\
> systemd-timedated reads /etc/adjtime, and depending on the contents of the file,
  sets the clock to either UTC or local time.
  Create the /etc/adjtime file with the following contents if your hardware clock is set to local time:
    cat > /etc/adjtime << "EOF"
    0.0 0 0.0
    0
    LOCAL
    EOF
  If /etc/adjtime isn't present at first boot, systemd-timedated will assume that hardware clock is set to UTC
  and adjust the file according to that.

> You can also use the timedatectl utility to tell systemd-timedated if your hardware clock is set to UTC or local time:
    timedatectl set-local-rtc 1
  timedatectl can also be used to change system time and time zone.

> To change your current system time, issue:
    timedatectl set-time YYYY-MM-DD HH:MM:SS
  The hardware clock will also be updated accordingly.

> To change your current time zone, issue:
    timedatectl set-timezone TIMEZONE

> You can get a list of available time zones by running:
    timedatectl list-timezones

> Starting with version 213, systemd ships a daemon called systemd-timesyncd 
  which can be used to synchronize the system time with remote NTP servers.
  Starting with systemd version 216, the systemd-timesyncd daemon is enabled by default.
  If you want to disable it, issue the following command:
    systemctl disable systemd-timesyncd
  The /etc/systemd/timesyncd.conf file can be used to change the NTP servers that systemd-timesyncd synchronizes with.
  Please note that when system clock is set to Local Time, systemd-timesyncd won't update hardware clock.
"""

console_help = """\
> The systemd-vconsole-setup service reads the /etc/vconsole.conf file for configuration information. 
  Examine the output of localectl list-keymaps for a list of valid console keymaps. 
  Look in the /usr/share/consolefonts directory for valid screen fonts.

> The /etc/vconsole.conf file should contain lines of the form: VARIABLE="value".
  The following variables are recognized:
  KEYMAP
    This variable specifies the key mapping table for the keyboard. If unset, it defaults to us.
  KEYMAP_TOGGLE
    This variable can be used to configure a second toggle keymap and is unset by default.
  FONT
    This variable specifies the font used by the virtual console.
  FONT_MAP
    This variable specifies the console map to be used.
  FONT_UNIMAP
    This variable specifies the Unicode font map.

> An example for a German keyboard and console is given below:
    cat > /etc/vconsole.conf << "EOF"
    KEYMAP=de-latin1
    FONT=Lat2-Terminus16
    EOF

> You can change KEYMAP value at runtime by using the localectl utility:
    localectl set-keymap MAP

> You can also use localectl utility with the corresponding parameters
  to change X11 keyboard layout, model, variant and options:
    localectl set-x11-keymap LAYOUT [MODEL] [VARIANT] [OPTIONS]

> To list possible values for localectl set-x11-keymap parameters, run localectl with parameters listed below:
  list-x11-keymap-models
    Shows known X11 keyboard mapping models.
  list-x11-keymap-layouts
    Shows known X11 keyboard mapping layouts.
  list-x11-keymap-variants
    Shows known X11 keyboard mapping variants.
  list-x11-keymap-options
    Shows known X11 keyboard mapping options.
"""

locale_help = """
> The /etc/locale.conf file below sets some environment variables necessary for native language support.
  Setting them properly results in:
  a) The output of programs being translated into your native language.
  b) The correct classification of characters into letters, digits and other classes. This is necessary for bash to properly accept non-ASCII characters in command lines in non-English locales.
  c) The correct alphabetical sorting order for the country.
  d) The appropriate default paper size.
  e) The correct formatting of monetary, time, and date values.

> Replace <ll> below with the two-letter code for your desired language (e.g., “en”),
  and <CC> with the two-letter code for the appropriate country (e.g., “GB”),
  <charmap> should be replaced with the canonical charmap for your chosen locale,
  Optional modifiers such as “@euro” may also be present.

> The list of all locales supported by Glibc can be obtained by running the following command:
    locale -a

> To determine the canonical name, run the following command,
  where <locale name> is the output given by locale -a for your preferred locale (“en_GB.iso88591” in our example).
    LC_ALL=<locale name> locale charmap
  For the “en_GB.iso88591” locale, the above command will print: ISO-8859-1.

> Once the proper locale settings have been determined, create the /etc/locale.conf file:
    cat > /etc/locale.conf << "EOF"
    LANG=<ll>_<CC>.<charmap><@modifiers>
    EOF

> Note that you can modify /etc/locale.conf with the systemd localectl utility.
  To use localectl for the example above, run:
    localectl set-locale LANG="<ll>_<CC>.<charmap><@modifiers>"

> You can also specify other language specific environment variables
  such as LANG, LC_CTYPE, LC_NUMERIC or any other environment variable from locale output.
  Just separate them with a space.
  An example where LANG is set as en_US.UTF-8 but LC_CTYPE is set as just en_US is:
    localectl set-locale LANG="en_US.UTF-8" LC_CTYPE="en_US"
  Please note that the localectl command doesn't work in the chroot environment.
  It can only be used after the LFS system is booted with systemd.

> The “C” (default) and “en_US” (the recommended one for United States English users) locales are different.
  “C” uses the US-ASCII 7-bit character set, and treats bytes with the high bit set as invalid characters.
  It's suggested that you use the “C” locale only if you are certain that you will never need 8-bit characters.
"""

inputrc_help = """\
> The inputrc file is the configuration file for the readline library,
  which provides editing capabilities while the user is entering a line from the terminal.
  It works by translating keyboard inputs into specific actions.
  Readline is used by bash and most other shells as well as many other applications.

> Most people do not need user-specific functionality so the command below creates a global /etc/inputrc
  used by everyone who logs in.
  If you later decide you need to override the defaults on a per user basis,
  you can create a .inputrc file in the user's home directory with the modified mappings.
"""

systemd_help = """\
> The /etc/systemd/system.conf file contains a set of options to control basic systemd operations. 
  The default file has all entries commented out with the default settings indicated. 
  See the systemd-system.conf(5) manual page for details on each configuration option.
  
> The normal behavior for systemd is to clear the screen at the end of the boot sequence.
  If desired, this behavior may be changed by running the following command:
    mkdir -pv /etc/systemd/system/getty@tty1.service.d
    cat > /etc/systemd/system/getty@tty1.service.d/noclear.conf << EOF
    [Service]
    TTYVTDisallocate=no
    EOF
  The boot messages can always be reviewed by using the journalctl -b command as the root user.

> By default, /tmp is created as a tmpfs. If this is not desired,
  it can be overridden by executing the following command:
    ln -sfv /dev/null /etc/systemd/system/tmp.mount
  Alternatively, if a separate partition for /tmp is desired, specify that partition in a /etc/fstab entry.
  Do not create the symbolic link above if a separate partition is used for /tmp.
  This will prevent the root file system (/) from being remounted r/w and make the system unusable when booted.

> There are several services that create or delete files or directories:
  a). systemd-tmpfiles-clean.service
  b). systemd-tmpfiles-setup-dev.service
  c). systemd-tmpfiles-setup.service
  The system location for the configuration files is /usr/lib/tmpfiles.d/*.conf.
  The local configuration files are in /etc/tmpfiles.d.
  Files in /etc/tmpfiles.d override files with the same name in /usr/lib/tmpfiles.d.
  See tmpfiles.d(5) manual page for file format details.

> Logging on a system booted with systemd is handled with systemd-journald (by default),
  rather than a typical unix syslog daemon. 
  Here are some examples of frequently used commands:
  a) journalctl -r: shows all contents of the journal in reverse chronological order.
  b) journalctl -u UNIT: shows the journal entries associated with the specified UNIT file.
  c) journalctl -b[=ID] -r: shows the journal entries since last successful boot (or for boot ID) in reverse chronological order.
  d) journalctl -f: provides functionality similar to tail -f (follow).


> Core dumps are useful to debug crashed programs, especially when a daemon process crashes. 
  On systemd booted systems the core dumping is handled by systemd-coredump. 
  It will log the core dump in the journal and store the core dump itself in /var/lib/systemd/coredump.
  Here are some examples of frequently used commands:
  a) coredumpctl -r: lists all core dumps in reverse chronological order.
  b) coredumpctl -1 info: shows the information from the last core dump.
  c) coredumpctl -1 debug: loads the last core dump into GDB.

  The maximum disk space used by core dumps can be limited by creating a configuration file
  in /etc/systemd/coredump.conf.d. For example:
    mkdir -pv /etc/systemd/coredump.conf.d
    cat > /etc/systemd/coredump.conf.d/maxuse.conf << EOF
    [Coredump]
    MaxUse=5G
    EOF
  See the systemd-coredump(8), coredumpctl(1), and coredump.conf.d(5) manual pages for more information.

> Beginning with systemd-230, all user processes are killed when a user session is ended,
  even if nohup is used, or the process uses the daemon() or setsid() functions.
  The new behavior may cause issues if you depend on long running programs (e.g., screen or tmux)
  to remain active after ending your user session.
  There are three ways to enable lingering processes to remain after a user session is ended.
  a) Enable process lingering for only selected users:
        loginctl enable-linger 
        systemd-run --scope --user /usr/bin/screen
    This has the advantage of explicitly allowing and disallowing processes to run after the user session has ended,
    but breaks backwards compatibility with tools like nohup and utilities that use daemon().
  b) Enable system-wide process lingering: 
    You can set KillUserProcesses=no in /etc/systemd/logind.conf to enable process lingering globally for all users. 
    This has the benefit of leaving the old method available to all users at the expense of explicit control.
  c) Disable at build-time:
    You can disable lingering by default while building systemd by
    adding the switch -Ddefault-kill-user-processes=false to the meson command for systemd.
    This completely disables the ability of systemd to kill user processes at session end.
"""


etc_adjtime = """
0.0 0 0.0
0
LOCAL
"""

etc_inputrc = """
# Begin /etc/inputrc
# Modified by Chris Lynn <roryo@roryo.dynup.net>

# Allow the command prompt to wrap to the next line
set horizontal-scroll-mode Off

# Enable 8-bit input
set meta-flag On
set input-meta On

# Turns off 8th bit stripping
set convert-meta Off

# Keep the 8th bit for display
set output-meta On

# none, visible or audible
set bell-style none

# All of the following map the escape sequence of the value
# contained in the 1st argument to the readline specific functions
"\eOd": backward-word
"\eOc": forward-word

# for linux console
"\e[1~": beginning-of-line
"\e[4~": end-of-line
"\e[5~": beginning-of-history
"\e[6~": end-of-history
"\e[3~": delete-char
"\e[2~": quoted-insert

# for xterm
"\eOH": beginning-of-line
"\eOF": end-of-line

# for Konsole
"\e[H": beginning-of-line
"\e[F": end-of-line

# End /etc/inputrc
"""

etc_shells = """
# Begin /etc/shells

/bin/sh
/bin/bash
{shell.bin}

# End /etc/shells
"""


etc_fstab = """
# Begin /etc/fstab

# file system  mount-point    type     options             dump  fsck
#                                                                order

/dev/<xxx>     /              <fff>    defaults            1     1
/dev/<yyy>     swap           swap     pri=1               0     0
proc           /proc          proc     nosuid,noexec,nodev 0     0
sysfs          /sys           sysfs    nosuid,noexec,nodev 0     0
devpts         /dev/pts       devpts   gid=5,mode=620      0     0
tmpfs          /run           tmpfs    defaults            0     0
devtmpfs       /dev           devtmpfs mode=0755,nosuid    0     0
tmpfs          /dev/shm       tmpfs    nosuid,nodev        0     0
cgroup2        /sys/fs/cgroup cgroup2  nosuid,noexec,nodev 0     0

# End /etc/fstab
"""


class EtcConfig(object):
    adjtime = etc_adjtime
    inputrc = etc_inputrc
    shells = etc_shells
    fstab = etc_fstab

    def __init__(self):
        raise RuntimeError('Should not use object')

