#!/bin/sh
target=arm-none-eabi
srcdir=/source/gcc
. /source/gcc/config.gcc
printf 'xm_file=%s\nxm_defines=%s\ntm_file=%s\ntm_defines=%s\n' "$xm_file" "$xm_defines" "$tm_file" "$tm_defines"
