# 0 "/inputs/gcc-source/libgcc/config/arm/crti.S"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/inputs/gcc-source/libgcc/config/arm/crti.S"
# Copyright (C) 2001-2024 Free Software Foundation, Inc.
# Written By Nick Clifton

# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.

# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# Under Section 7 of GPL version 3, you are granted additional
# permissions described in the GCC Runtime Library Exception, version
# 3.1, as published by the Free Software Foundation.

# You should have received a copy of the GNU General Public License and
# a copy of the GCC Runtime Library Exception along with this program;
# see the files COPYING3 and COPYING.RUNTIME respectively. If not, see
# <http:







# This file just make a stack frame for the contents of the .fini and
# .init sections. Users may put any desired instructions in those
# sections.
# 45 "/inputs/gcc-source/libgcc/config/arm/crti.S"
 .eabi_attribute 25, 1


 # Note - this macro is complemented by the FUNC_END macro
 # in crtn.S. If you change this macro you must also change
 # that macro match.
.macro FUNC_START

 .thumb

 push {r3, r4, r5, r6, r7, lr}







.endm

 .section ".init"
 .align 2
 .global _init

 .thumb_func

 .type _init,function
_init:
 FUNC_START


 .section ".fini"
 .align 2
 .global _fini

 .thumb_func

 .type _fini,function
_fini:
 FUNC_START

# end of crti.S
