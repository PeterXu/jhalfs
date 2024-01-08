#!/bin/bash

set -e

. ./load-todo.sh
check_env_root

[ "$LFS" = "" ] && exit 1

mkdir -pv $LFS/{etc,var} $LFS/usr/{bin,lib,sbin}

cd $LFS
for i in bin lib sbin; do
  ln -sv usr/$i $LFS/$i
done

case $(uname -m) in
  x86_64) mkdir -pv $LFS/lib64 ;;
esac

mkdir -pv $LFS/tools
