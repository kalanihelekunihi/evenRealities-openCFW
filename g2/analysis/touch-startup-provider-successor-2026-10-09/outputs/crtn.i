# 0 "/inputs/gcc-source/libgcc/config/arm/crtn.S"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/inputs/gcc-source/libgcc/config/arm/crtn.S"
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
# 36 "/inputs/gcc-source/libgcc/config/arm/crtn.S"
 .eabi_attribute 25, 1


# This file just makes sure that the .fini and .init sections do in
# fact return. Users may put any desired instructions in those sections.
# This file is the last thing linked into any executable.

 # Note - this macro is complemented by the FUNC_START macro
 # in crti.S. If you change this macro you must also change
 # that macro match.

 # Note - we do not try any fancy optimizations of the return
 # sequences here, it is just not worth it. Instead keep things
 # simple. Restore all the save registers, including the link
 # register and then perform the correct function return instruction.
 # We also save/restore r3 to ensure stack alignment.
.macro FUNC_END

 .thumb

 pop {r3, r4, r5, r6, r7}
 pop {r3}
 mov lr, r3
# 67 "/inputs/gcc-source/libgcc/config/arm/crtn.S"
 bx lr



.endm


 .section ".init"
 ;;
 FUNC_END

 .section ".fini"
 ;;
 FUNC_END

# end of crtn.S
