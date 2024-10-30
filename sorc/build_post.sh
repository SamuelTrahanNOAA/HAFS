#!/bin/sh
set -eux
source ./machine-setup.sh > /dev/null 2>&1
if [ $target = wcoss2 ]; then source ../versions/build.ver; fi
cwd=$(pwd)

cp -fp customizations/hafs_post.fd/gaea.lua hafs_post.fd/modulefiles/gaea.lua
cd hafs_post.fd/tests
./compile_upp.sh

exit
