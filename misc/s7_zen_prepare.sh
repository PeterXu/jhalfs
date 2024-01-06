#!/bin/bash
# Should run in chroot.

set -e

. ./load-todo.sh

do_create_dir() {
  [ -e /boot ] && return 1

  # root-dir
  mkdir -pv /{boot,home,mnt,opt,srv}

  # Default dir perm is: 755,
  mkdir -pv /etc/{opt,sysconfig}
  mkdir -pv /lib/firmware
  mkdir -pv /media/{floppy,cdrom}
  mkdir -pv /usr/{,local/}{include,src}
  mkdir -pv /usr/local/{bin,lib,sbin}
  mkdir -pv /usr/{,local/}share/{color,dict,doc,info,locale,man}
  mkdir -pv /usr/{,local/}share/{misc,terminfo,zoneinfo}
  mkdir -pv /usr/{,local/}share/man/man{1..8}
  mkdir -pv /var/{cache,local,log,mail,opt,spool}
  mkdir -pv /var/lib/{color,misc,locate}

  ln -sfv /run /var/run
  ln -sfv /run/lock /var/lock

  # 1. to assure not everyone could enter /root,
  # 2. to assure everyone could write in /tmp and /var/tmp, but
  #    couldnot delete others' files.
  install -dv -m 0750 /root
  install -dv -m 1777 /tmp /var/tmp

  # But /root,/tmp,/var/tmp are different.
  # Refer: https://refspecs.linuxfoundation.org/fhs.shtml.
  # Some others: /usr/local/games, /usr/share/games.
  # FHS donot need /usr/lib64.
}

do_create_files() {
  [ -e /etc/hosts ] && return 1

  # compatible with old system.
  ln -sv /proc/self/mounts /etc/mtab

  #/etc/hosts
  cat > /etc/hosts << EOF
127.0.0.1  localhost $(hostname)
::1        localhost
EOF

  #/etc/passwd, but root-password delay to set.
  cat > /etc/passwd << "EOF"
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/dev/null:/usr/bin/false
daemon:x:6:6:Daemon User:/dev/null:/usr/bin/false
messagebus:x:18:18:D-Bus Message Daemon User:/run/dbus:/usr/bin/false
systemd-journal-gateway:x:73:73:systemd Journal Gateway:/:/usr/bin/false
systemd-journal-remote:x:74:74:systemd Journal Remote:/:/usr/bin/false
systemd-journal-upload:x:75:75:systemd Journal Upload:/:/usr/bin/false
systemd-network:x:76:76:systemd Network Management:/:/usr/bin/false
systemd-resolve:x:77:77:systemd Resolver:/:/usr/bin/false
systemd-timesync:x:78:78:systemd Time Synchronization:/:/usr/bin/false
systemd-coredump:x:79:79:systemd Core Dumper:/:/usr/bin/false
uuidd:x:80:80:UUID Generation Daemon User:/dev/null:/usr/bin/false
systemd-oom:x:81:81:systemd Out Of Memory Daemon:/:/usr/bin/false
nobody:x:65534:65534:Unprivileged User:/dev/null:/usr/bin/false
EOF

  #/etc/group
  cat > /etc/group << "EOF"
root:x:0:
bin:x:1:daemon
sys:x:2:
kmem:x:3:
tape:x:4:
tty:x:5:
daemon:x:6:
floppy:x:7:
disk:x:8:
lp:x:9:
dialout:x:10:
audio:x:11:
video:x:12:
utmp:x:13:
usb:x:14:
cdrom:x:15:
adm:x:16:
messagebus:x:18:
systemd-journal:x:23:
input:x:24:
mail:x:34:
kvm:x:61:
systemd-journal-gateway:x:73:
systemd-journal-remote:x:74:
systemd-journal-upload:x:75:
systemd-network:x:76:
systemd-resolve:x:77:
systemd-timesync:x:78:
systemd-coredump:x:79:
uuidd:x:80:
systemd-oom:x:81:
wheel:x:97:
users:x:999:
nogroup:x:65534:
EOF

  # refer: https://refspecs.linuxfoundation.org/lsb.shtml 
  # LSB only suggests create user-group(root) by ID-0 and user-group(bin) by ID-1.
  # ID-5 often for tty-group, and systemd set devpts to 5.
  # ID-65534 for NFS and user-namespace by kernel(nobody/nogroup).

  # create some testing group(could be deleted when not-use)
  echo "tester:x:101:101::/home/tester:/bin/bash" >> /etc/passwd
  echo "tester:x:101:" >> /etc/group
  install -o tester -d /home/tester

  # now login again and no prompt: I have no name!
  echo "You could login again by: 'exec /usr/bin/bash --login'"

  # initilize log file: 
  #   wtmp for all login/logout,
  #   lastlog for each user's last login time,
  #   faillog for all failure login,
  #   btmp for all error login,
  # and /run/utmp for current login user(created by init)
  touch /var/log/{btmp,lastlog,faillog,wtmp}
  chgrp -v utmp /var/log/lastlog
  chmod -v 664  /var/log/lastlog
  chmod -v 600  /var/log/btmp
}


#===== compile libraries=======

# in chroot
go_gettext() {
  check_pkg "gettext" || return
  check_nop || return

  mkdir -v build
  ./configure --disable-shared

  make
  cp -v gettext-tools/src/{msgfmt,msgmerge,xgettext} /usr/bin
}

# in chroot
go_bison() {
  check_pkg "bison" || return
  check_nop || return

  ver=$(basename $(pwd) | cut -d '-' -f2)

  mkdir -v build
  ./configure \
    --prefix=/usr \
    --docdir=/usr/share/doc/bison-$ver

  make
  make install
}

# in chroot
go_perl() {
  check_pkg "perl" || return
  check_nop || return

  ver=$(basename $(pwd) | cut -d '-' -f2 | cut -d '.' -f1-2)
  M=$(echo $ver | cut -d '.' -f1)

  mkdir -v build
  sh Configure \
    -des                                        \
    -Dprefix=/usr                               \
    -Dvendorprefix=/usr                         \
    -Duseshrplib                                \
    -Dprivlib=/usr/lib/perl$M/$ver/core_perl     \
    -Darchlib=/usr/lib/perl$M/$ver/core_perl     \
    -Dsitelib=/usr/lib/perl$M/$ver/site_perl     \
    -Dsitearch=/usr/lib/perl$M/$ver/site_perl    \
    -Dvendorlib=/usr/lib/perl$M/$ver/vendor_perl \
    -Dvendorarch=/usr/lib/perl$M/$ver/vendor_perl

  make
  make install
}

# in chroot
go_python() {
  check_pkg "Python" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --enable-shared \
    --without-ensurepip

  make
  make install
}

# in chroot
go_texinfo() {
  check_pkg "texinfo" || return
  check_nop || return

  mkdir -v build
  ./configure --prefix=/usr

  make
  make install
}

go_util_linux() {
  check_pkg "util-linux" || return
  check_nop || return

  ver=$(basename $(pwd) | cut -d '-' -f2)

  mkdir -v build
  ./configure ADJTIME_PATH=/var/lib/hwclock/adjtime    \
            --libdir=/usr/lib    \
            --runstatedir=/run   \
            --docdir=/usr/share/doc/util-linux-$ver \
            --disable-chfn-chsh  \
            --disable-login      \
            --disable-nologin    \
            --disable-su         \
            --disable-setpriv    \
            --disable-runuser    \
            --disable-pylibmount \
            --disable-static     \
            --without-python

  make
  make install
}

do_cleanup() {
  local items="gettext bison perl python texinfo util-linux"
  for item in $items; do
    local ret=0
    check_pkg "$item" || ret=$?
    if [ $ret -eq 2 ]; then
      local cwd=$(pwd)
      rm -rf "$cwd/build" || echo
    fi
  done
}

do_clean_unused() {
  [ ! -e /sources/wspace ] && return

  # clean temporal docs(about 35MB)
  rm -rf /usr/share/{info,man,doc}/*
  # .la only for libltdl but LFS not use.
  find /usr/{lib,libexec} -name \*.la -delete
  # clean tools
  rm -rf /tools

  # clean temp build files
  rm -rf /sources/all
  rm -rf /sources/allone
}

do_mycopy() {
  if [ "$LFS" != "" ]; then
    sudo mkdir -p $LFS/sources/wspace/
    sudo cp -f $(pwd)/load-todo.sh $LFS/sources/wspace/
    sudo cp -f $(pwd)/s7_zen_prepare.sh $LFS/sources/wspace/
  fi
}

ALL_MISC="mycopy"
ALL_ACTS="create_dir create_files cleanup clean_unused"
ALL_LIBS="gettext bison perl python texinfo util_linux"
check_todo "zen" "$1"

