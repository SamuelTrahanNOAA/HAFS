#!/bin/sh
set -eux
source ./machine-setup.sh > /dev/null 2>&1
if [ $target = wcoss2 ]; then source ../versions/build.ver; fi
cwd=$(pwd)

cp -fp customizations/hafs_tracker.fd/machine-setup.sh hafs_tracker.fd/src/.
cp -fp customizations/hafs_tracker.fd/gaeaC5.lua hafs_tracker.fd/modulefiles/.

export BUILD_TYPE=${BUILD_TYPE:-RELEASE}

cd hafs_tracker.fd/src
./build_all_cmake.sh

exit
