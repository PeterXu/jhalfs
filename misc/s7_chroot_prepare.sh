#!/bin/bash

set -e

. ./load-todo.sh

detect_root_lfs() {
  [ "$(whoami)" = "root" ] || return 1
  [ "$LFS" = "" ] && return 1
  [ -e "$LFS/lost+found" ] || return 1
  [ -e "$LFS/sources/wspace" ] || return 1
  return 0
}

do_change_root() {
  detect_root_lfs || return

  chown -R root:root $LFS/{usr,lib,var,etc,bin,sbin,tools}
  case $(uname -m) in
    x86_64) chown -R root:root $LFS/lib64 ;;
  esac
}

do_prepare_vfs() {
  detect_root_lfs || return

  mkdir -pv $LFS/{dev,proc,sys,run}

  # mount dev(devtmpfs)
  mount -v --bind /dev $LFS/dev

  # mount pts/proc/sysfs/tmpfs
  mount -v --bind /dev/pts $LFS/dev/pts
  mount -vt proc proc $LFS/proc
  mount -vt sysfs sysfs $LFS/sys
  mount -vt tmpfs tmpfs $LFS/run

  # mount tmpfs explicitly(compatiable with all system)
  if [ -h $LFS/dev/shm ]; then
    mkdir -pv $LFS/$(readlink $LFS/dev/shm)
  else
    mount -t tmpfs -o nosuid,nodev tmpfs $LFS/dev/shm
  fi
}

do_enter_chroot() {
  detect_root_lfs || return

  chroot "$LFS" /usr/bin/env -i   \
    HOME=/root                  \
    TERM="$TERM"                \
    PS1='(lfs chroot) \u:\w\$ ' \
    PATH=/usr/bin:/usr/sbin     \
    /bin/bash --login

  # /tools/bin not in PATH
  # so donot be able to use crosstool.

  # Here bash will prompt: I have no name!
  # This is because no /etc/passwd now.
}

# not in chroot
do_backup() {
  detect_root_lfs || return

  # first unmount vfs
  mountpoint -q $LFS/dev/shm && umount $LFS/dev/shm || echo
  umount $LFS/dev/pts || echo
  umount $LFS/{sys,proc,run,dev} || echo

  local backup_tar="lfs-temp-tools-12.0-systemd.tar"
  [ -f "$HOME/$backup_tar" ] && return

  cd $LFS
  tar -cpf $HOME/$backup_tar .
}

# not in chroot
do_restore() {
  detect_root_lfs || return

  local backup_tar="lfs-temp-tools-12.0-systemd.tar"
  [ -f "$HOME/$backup_tar" ] || return

  cd $LFS
  rm -rf ./*
  tar -xpf $HOME/$backup_tar
}


ALL_ACTS="change_root prepare_vfs enter_chroot backup restore"
check_todo "nop" "$1"

