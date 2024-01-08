#!/bin/bash

set -e

. ./load-todo.sh
check_env_root

[ "$LFS" = "" ] && exit 1

groupadd lfs
useradd -s /bin/bash -g lfs -m -k /dev/null lfs

#passwd lfs

chown -v lfs $LFS/{usr{,/*},lib,var,etc,bin,sbin,tools,sources}
case $(uname -m) in
  x86_64) chown -v lfs $LFS/lib64 ;;
esac

#su - lfs
