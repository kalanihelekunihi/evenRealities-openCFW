#!/bin/sh
# Source the authentic target selector, retaining its output as build evidence.
host=arm-none-eabi
srcdir=/source/libgcc
. /source/libgcc/config.host
printf 'tm_file=%s\ntm_define=%s\ntm_defines=%s\ntmake_file=%s\n' "$tm_file" "$tm_define" "$tm_defines" "$tmake_file"
