#!/bin/bash

set -e

[ ! "$(whoami)" = "lfs" ] && echo "WARN: not user - lfs!" && exit 1

# should by lfs
cat > ~/.bash_profile << "EOF"
exec env -i HOME=$HOME TERM=$TERM PS1='\u:\w\$ ' /bin/bash
EOF

# should set LFS with string not var
echo "INFO: add env-LFS(default /media/ddisk) to .bashrc!"
cat > ~/.bashrc << "EOF"
set +h
umask 022
LFS=/media/ddisk
LC_ALL=POSIX
LFS_TGT=$(uname -m)-lfs-linux-gnu
PATH=/usr/bin
if [ ! -L /bin ]; then PATH=/bin:$PATH; fi
PATH=$LFS/tools/bin:$PATH
CONFIG_SITE=$LFS/usr/share/config.site
export LFS LC_ALL LFS_TGT PATH CONFIG_SITE
EOF

source ~/.bash_profile
