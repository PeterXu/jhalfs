#!/bin/bash

set -e

. ./load-todo.sh


go_binutils() {
  check_pkg "binutils" || return
  check_nop || return

  mkdir -v build
  cd       build
  ../configure          \
    --prefix=$LFS/tools \
    --with-sysroot=$LFS \
    --target=$LFS_TGT   \
    --disable-nls       \
    --enable-gprofng=no \
    --disable-werror

  make
  make install
}

go_gcc() {
  # get glibc version
  check_pkg "glibc" || echo
  ver=$(basename $(pwd) | cut -d '-' -f2)

  # first check dependencies
  check_pkg "gcc" || return
  [ -e "mpfr" -a -e "gmp" -a -e "mpc" ] && extra_dep=1 || extra_dep=0
  if [ $extra_dep -ne 1 ]; then
    check_pkg "mpfr"
    d_mpfr=$(pwd)
    check_pkg "gmp"
    d_gmp=$(pwd)
    check_pkg "mpc"
    d_mpc=$(pwd)
  fi

  # then enter gcc
  check_pkg "gcc" || return
  check_nop || return
  echo "glibc version: $ver"

  if [ $extra_dep -ne 1 ]; then
    mv -v $d_mpfr mpfr
    mv -v $d_gmp gmp
    mv -v $d_mpc mpc
  fi

  # change lib to lib64 for x86_64.
  case $(uname -m) in
  x86_64)
    sed -e '/m64=/s/lib64/lib/' -i.orig gcc/config/i386/t-linux64
    ;;
  esac

  mkdir -v build
  cd       build
  ../configure                \
    --target=$LFS_TGT         \
    --prefix=$LFS/tools       \
    --with-glibc-version=$ver \
    --with-sysroot=$LFS       \
    --with-newlib             \
    --without-headers         \
    --enable-default-pie      \
    --enable-default-ssp      \
    --disable-nls             \
    --disable-shared          \
    --disable-multilib        \
    --disable-threads         \
    --disable-libatomic       \
    --disable-libgomp         \
    --disable-libquadmath     \
    --disable-libssp          \
    --disable-libvtv          \
    --disable-libstdcxx       \
    --enable-languages=c,c++

  make
  make install

  # To generate $LFS/usr/include/limits.h
  cd ..
  cat gcc/limitx.h gcc/glimits.h gcc/limity.h > \
    `dirname $($LFS_TGT-gcc -print-libgcc-file-name)`/include/limits.h
}

# linux-api headers:
#   /usr/include/asm/*.h,
#   /usr/include/asm-generic/*.h,
#   /usr/include/drm/*.h,
#   /usr/include/linux/*.h,
#   /usr/include/misc/*.h,
#   /usr/include/mtd/*.h,
#   /usr/include/rdma/*.h, 
#   /usr/include/scsi/*.h,
#   /usr/include/sound/*.h,
#   /usr/include/video/*.h,
#   /usr/include/xen/*.h
go_linux_api() {
  check_pkg "linux" || return
  check_nop || return

  mkdir -v build #nop
  make mrproper
  make headers
  find usr/include -type f ! -name '*.h' -delete
  cp -rv usr/include $LFS/usr
}

go_glibc() {
  check_pkg "glibc" || return
  check_nop || return

  ver=$(basename $(pwd) | cut -d '-' -f2)
  fpatch="glibc-$ver-fhs-1.patch"
  echo "INFO: checking $fpatch"
  if [ -f ../../$fpatch ]; then
    patch -Np1 -i ../../$fpatch && echo "INFO: patch OK" || echo "WARN: patch failed"
  fi

  case $(uname -m) in
    i?86)   ln -sfv ld-linux.so.2 $LFS/lib/ld-lsb.so.3
    ;;
    x86_64) ln -sfv ../lib/ld-linux-x86-64.so.2 $LFS/lib64
            ln -sfv ../lib/ld-linux-x86-64.so.2 $LFS/lib64/ld-lsb-x86-64.so.3
    ;;
  esac

  mkdir -v build
  cd       build

  # install ldconfig/sln to /usr/sbin
  echo "rootsbindir=/usr/sbin" > configparms

  # use libc_cv_slibdir to install /usr/lib not /lib64,
  ../configure                           \
      --prefix=/usr                      \
      --host=$LFS_TGT                    \
      --build=$(../scripts/config.guess) \
      --enable-kernel=4.14               \
      --with-headers=$LFS/usr/include    \
      libc_cv_slibdir=/usr/lib

  # use -j1 to avoid failure
  make
  make -j1
  make DESTDIR=$LFS install
  
  # update loading path in ldd
  sed '/RTLDLIST=/s@/usr@@g' -i $LFS/usr/bin/ldd
}

go_libstdcpp() {
  check_pkg "gcc" "build_stdcpp" || return
  check_nop || return
  ver=$(basename $(pwd) | cut -d '-' -f2)

  mkdir -v build_stdcpp
  cd       build_stdcpp
  ../libstdc++-v3/configure         \
    --host=$LFS_TGT                 \
    --build=$(../config.guess)      \
    --prefix=/usr                   \
    --disable-multilib              \
    --disable-nls                   \
    --disable-libstdcxx-pch         \
    --with-gxx-include-dir=/tools/$LFS_TGT/include/c++/$ver

  make
  make DESTDIR=$LFS install
  rm -v $LFS/usr/lib/lib{stdc++,stdc++fs,supc++}.la
}

do_clean() {
  cd $ALL || return
  rm -rf $ALL/binutils*
  rm -rf $ALL/gcc*
  rm -rf $ALL/linux*
  rm -rf $ALL/glibc*
}

do_test() {
  # check glibc
  cd /tmp/
  echo 'int main(){}' | $LFS_TGT-gcc -xc -
  readelf -l a.out | grep ld-linux
  #OK: [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
  rm -v a.out
}


ALL_ACTS="test clean"
ALL_LIBS="binutils gcc linux_api glibc libstdcpp"
check_todo "cross" "$1"

