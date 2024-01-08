#!/bin/bash

set -e

. ./load-todo.sh


go_m4() {
  check_pkg "m4" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_ncurses() {
  check_pkg "ncurses" || return
  check_nop || return

  # use gawk
  sed -i s/mawk// configure

  # make tic
  mkdir -v build
  pushd build
  ../configure
  make -C include
  make -C progs tic
  popd

  # make 
  ./configure \
    --prefix=/usr                \
    --host=$LFS_TGT              \
    --build=$(./config.guess)    \
    --mandir=/usr/share/man      \
    --with-manpage-format=normal \
    --with-shared                \
    --without-normal             \
    --with-cxx-shared            \
    --without-debug              \
    --without-ada                \
    --disable-stripping          \
    --enable-widec

  make
  make DESTDIR=$LFS TIC_PATH=$(pwd)/build/progs/tic install
  echo "INPUT(-lncursesw)" > $LFS/usr/lib/libncurses.so
}

go_bash() {
  check_pkg "bash" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr                      \
    --build=$(sh support/config.guess) \
    --host=$LFS_TGT                    \
    --without-bash-malloc

  make
  make DESTDIR=$LFS install
  ln -sv bash $LFS/bin/sh
}

go_coreutils() {
  check_pkg "coreutils" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr                     \
    --host=$LFS_TGT                   \
    --build=$(./build-aux/config.guess) \
    --enable-install-program=hostname \
    --enable-no-install-program=kill,uptime \
    gl_cv_macro_MB_CUR_MAX_good=y

  make
  make DESTDIR=$LFS install

  # move: some programs required
  mv -v $LFS/usr/bin/chroot              $LFS/usr/sbin
  mkdir -pv $LFS/usr/share/man/man8
  mv -v $LFS/usr/share/man/man1/chroot.1 $LFS/usr/share/man/man8/chroot.8
  sed -i 's/"1"/"8"/'                    $LFS/usr/share/man/man8/chroot.8
}

go_diffutils() {
  check_pkg "diffutils" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_file() {
  check_pkg "file" || return
  check_nop || return

  # first to gen an copy.
  mkdir -v build
  pushd build
  ../configure --disable-bzlib      \
               --disable-libseccomp \
               --disable-xzlib      \
               --disable-zlib
  make
  popd

  # then to build
  ./configure --prefix=/usr --host=$LFS_TGT --build=$(./config.guess)

  make FILE_COMPILE=$(pwd)/build/src/file
  make DESTDIR=$LFS install
  rm -v $LFS/usr/lib/libmagic.la
}

go_findutils() {
  check_pkg "findutils" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr                   \
    --localstatedir=/var/lib/locate \
    --host=$LFS_TGT                 \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_gawk() {
  check_pkg "gawk" || return
  check_nop || return

  # remove unused
  sed -i 's/extras//' Makefile.in

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_grep() {
  check_pkg "grep" || return
  check_nop || return

  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_gzip() {
  check_pkg "gzip" || return
  check_nop || return

  mkdir -v build
  ./configure --prefix=/usr --host=$LFS_TGT

  make
  make DESTDIR=$LFS install
}

go_make() {
  check_pkg "make" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --without-guile \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_patch() {
  check_pkg "patch" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_sed() {
  check_pkg "sed" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr   \
    --host=$LFS_TGT \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_tar() {
  check_pkg "tar" || return
  check_nop || return

  mkdir -v build
  ./configure \
    --prefix=/usr                     \
    --host=$LFS_TGT                   \
    --build=$(./build-aux/config.guess)

  make
  make DESTDIR=$LFS install
}

go_xz() {
  check_pkg "xz" || return
  check_nop || return

  ver=$(basename $(pwd) | cut -d '-' -f2)

  mkdir -v build
  ./configure \
    --prefix=/usr                     \
    --host=$LFS_TGT                   \
    --build=$(./build-aux/config.guess) \
    --disable-static                  \
    --docdir=/usr/share/doc/xz-$ver

  make
  make DESTDIR=$LFS install
  rm -v $LFS/usr/lib/liblzma.la
}

go_binutils2() {
  check_pkg "binutils" "build2" || return
  check_nop || return

  # update old libtool
  sed '6009s/$add_dir//' -i ltmain.sh

  mkdir -v build2
  cd       build2
  ../configure                 \
    --prefix=/usr              \
    --build=$(../config.guess) \
    --host=$LFS_TGT            \
    --disable-nls              \
    --enable-shared            \
    --enable-gprofng=no        \
    --disable-werror           \
    --enable-64-bit-bfd

  make
  make DESTDIR=$LFS install
  rm -v $LFS/usr/lib/lib{bfd,ctf,ctf-nobfd,opcodes,sframe}.{a,la}
}

go_gcc2() {
  check_pkg "gcc" "build2" || return
  check_nop || return

  #some works done in s5
  #...

  #support pthread
  sed '/thread_header =/s/@.*@/gthr-posix.h/' \
    -i libgcc/Makefile.in libstdc++-v3/include/Makefile.in

  mkdir -v build2
  cd       build2
  ../configure                                     \
    --build=$(../config.guess)                     \
    --host=$LFS_TGT                                \
    --target=$LFS_TGT                              \
    LDFLAGS_FOR_TARGET=-L$PWD/$LFS_TGT/libgcc      \
    --prefix=/usr                                  \
    --with-build-sysroot=$LFS                      \
    --enable-default-pie                           \
    --enable-default-ssp                           \
    --disable-nls                                  \
    --disable-multilib                             \
    --disable-libatomic                            \
    --disable-libgomp                              \
    --disable-libquadmath                          \
    --disable-libsanitizer                         \
    --disable-libssp                               \
    --disable-libvtv                               \
    --enable-languages=c,c++

  make
  make DESTDIR=$LFS install
  ln -sv gcc $LFS/usr/bin/cc
}


#sum:17
ALL_LIBS="m4 ncurses bash coreutils diffutils file findutils gawk grep gzip make patch sed tar xz"
ALL_LIBS="$ALL_LIBS binutils2 gcc2" #the 2nd compiling
check_todo "cross" "$1"

