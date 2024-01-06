#!/bin/bash

set -e


SOURCES="unknown-sources"
ALL="unknown-all"

check_env_nop() {
  echo
}

# for compile cross
check_env_cross() {
  [ "$LFS" = "" ] && echo "WARN: no env LFS!" && exit 1
  [ "$LFS_TGT" = "" ] && echo "WARN: no env LFS_TGT" && exit 1
  [ "$(whoami)" = "lfs" ] || exit 1

  SOURCES="$LFS/sources"
  [ ! -e "$SOURCES" ] && exit 1
  ALL="$SOURCES/all"
  mkdir -pv "$ALL"
}

# for compile zen
check_env_zen() {
  SOURCES="/sources"
  [ ! -e "$SOURCES" ] && echo "WARN: no /sources!" && exit 1
  ALL="$SOURCES/allone"
  mkdir -pv "$ALL"
}


check_nop() {
  echo
  echo "--------------------------------"
  local _cwd=$(pwd)
  local _ver=$(basename $_cwd | cut -d '-' -f2)
  echo "INFO: pwd - $_cwd, version - $_ver"
  return 0
}

check_pkg() {
  local name="$1"
  local output="$2"
  local exclude="$3"
  [ "$output" = "" ] && output="build"
  [ "$exclude" = "" ] && exclude="X_NONE_X"
  echo "INFO: checking $name ..."

  local pkg="$(ls $SOURCES | grep ^$name | grep -v patch$ | grep -v $exclude)"
  [ "$pkg" = "" ] && return 1
  local z_pkg="$SOURCES/$pkg"
  echo "INFO: compress pkg - $z_pkg"
  [ ! -f "$z_pkg" ] && return 1

  cd $ALL || return 1
  pkg="$(ls . | grep ^$name)"
  [ "$pkg" = "" ] && (tar xf "$z_pkg")
  pkg="$(ls . | grep ^$name)"
  [ "$pkg" = "" ] && return 1

  local d_pkg="$ALL/$pkg"
  echo "INFO: decompress pkg - $d_pkg/$output"
  cd $d_pkg || return 1
  [ -e "$d_pkg/$output" ] && echo "WARN: build exists!" && return 2
  return 0
}

todo_misc() {
  local item="$1"
  echo
  echo "====BEGIN-MISC ($item)====="
  do_$item
  echo "====END-MISC ($item)====="
  echo
}

todo_action() {
  local item="$1"
  echo
  echo "====BEGIN-ACTION ($item)====="
  do_$item
  echo "====END-ACTION ($item)====="
  echo
}

todo_library() {
  export MAKEFLAGS="-j3"
  local items="$1"
  [ "$items" = "all" ] && items="$ALL_LIBS"
  for item in $items; do
    echo
    echo "====BEGIN-LIBARAY ($item)====="
    go_$item || echo "====SKIP-LIBRARY ($item)====="
    echo "====END-LIBRARY ($item)====="
    echo
  done
}

check_todo() {
  local mode="$1"
  local arg="$2"
  if [ "$arg" = "" ]; then
    [ "$ALL_MISC" = "" ] || echo "usage: $0 misc    ($ALL_MISC)"
    [ "$ALL_ACTS" = "" ] || echo "usage: $0 action  ($ALL_ACTS)"
    [ "$ALL_LIBS" = "" ] || echo "usage: $0 library (all: $ALL_LIBS)"
    echo
  else
    # first do misc without mode-checking
    for one in $ALL_MISC; do
      if [ "$one" = "$arg" ]; then
        todo_misc "$arg"
        return 0
      fi
    done

    # then do mode-checking
    case $mode in 
      nop)   check_env_nop;;
      cross) check_env_cross;;
      zen)   check_env_zen;;
      *)     echo "WARN: no mode set!(nop|cross|zen)" && exit 1;;
    esac

    # then do actions
    for act in $ALL_ACTS; do
      if [ "$act" = "$arg" ]; then
        todo_action "$arg"
        return 0
      fi
    done

    # then do library
    todo_library "$arg"
  fi
}

