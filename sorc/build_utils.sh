#!/bin/sh
set -eux
source ./machine-setup.sh > /dev/null 2>&1
if [ $target = wcoss2 ]; then source ../versions/build.ver; fi
cwd=$(pwd)

cp -fp ../modulefiles/hafs.hera.lua hafs_utils.fd/modulefiles/build.hera.intel.lua

if [[ ! -s hafs_utils.fd/modulefiles/build.gaea.intel.lua ]] ; then
    pushd hafs_utils.fd
    patch -p1 < ../customizations/hafs_utils.fd/gaea-c5-patch.diff
    popd
    cp -fp customizations/hafs_utils.fd/build.gaea-c5.intel.lua hafs_utils.fd/modulefiles/build.gaea.intel.lua
fi

cd hafs_utils.fd

./build_all.sh

exit
