# 0 "/source/libgcc/config/arm/lib1funcs.S"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/source/libgcc/config/arm/lib1funcs.S"
@ libgcc routines for ARM cpu.
@ Division routines, written by Richard Earnshaw, (rearnsha@armltd.co.uk)
# 27 "/source/libgcc/config/arm/lib1funcs.S"
 .syntax unified
# 42 "/source/libgcc/config/arm/lib1funcs.S"
 .eabi_attribute 25, 1
# 126 "/source/libgcc/config/arm/lib1funcs.S"
.macro cfi_pop advance, reg, cfa_offset

 .pushsection .debug_frame
 .byte 0x4
 .4byte \advance
 .byte (0xc0 | \reg)
 .byte 0xe
 .uleb128 \cfa_offset
 .popsection

.endm
.macro cfi_push advance, reg, offset, cfa_offset

 .pushsection .debug_frame
 .byte 0x4
 .4byte \advance
 .byte (0x80 | \reg)
 .uleb128 (\offset / -4)
 .byte 0xe
 .uleb128 \cfa_offset
 .popsection

.endm
.macro cfi_start start_label, end_label

 .pushsection .debug_frame
.Lstart_frame:
 .4byte .Lend_cie - .Lstart_cie @ Length of CIE
.Lstart_cie:
        .4byte 0xffffffff @ CIE Identifier Tag
        .byte 0x1 @ CIE Version
        .ascii "\0" @ CIE Augmentation
        .uleb128 0x1 @ CIE Code Alignment Factor
        .sleb128 -4 @ CIE Data Alignment Factor
        .byte 0xe @ CIE RA Column
        .byte 0xc @ DW_CFA_def_cfa
        .uleb128 0xd
        .uleb128 0x0

 .align 2
.Lend_cie:
 .4byte .Lend_fde-.Lstart_fde @ FDE Length
.Lstart_fde:
 .4byte .Lstart_frame @ FDE CIE offset
 .4byte \start_label @ FDE initial location
 .4byte \end_label-\start_label @ FDE address range
 .popsection

.endm
.macro cfi_end end_label

 .pushsection .debug_frame
 .align 2
.Lend_fde:
 .popsection
\end_label:

.endm



.macro RETLDM regs=, cond=, unwind=, dirn=ia
# 205 "/source/libgcc/config/arm/lib1funcs.S"
 .ifc "\regs",""
 ldr\cond pc, [sp], #8
 .else



 ldm\cond\dirn sp!, {\regs, pc}

 .endif

.endm
# 236 "/source/libgcc/config/arm/lib1funcs.S"
.macro do_it cond, suffix=""
.endm
.macro shift1 op, arg0, arg1, arg2
 mov \arg0, \arg1, \op \arg2
.endm


.macro shiftop name, dest, src1, src2, shiftop, shiftreg, tmp
 \name \dest, \src1, \src2, \shiftop \shiftreg
.endm





.macro ARM_LDIV0 name signed
 cmp r0, #0
 .ifc \signed, unsigned
 movne r0, #0xffffffff
 .else
 movgt r0, #0x7fffffff
 movlt r0, #0x80000000
 .endif
 b __aeabi_idiv0
.endm
# 273 "/source/libgcc/config/arm/lib1funcs.S"
.macro THUMB_LDIV0 name signed


 push {r0, lr}
 movs r0, #0
 bl __aeabi_idiv0
 @ We know we are not on armv4t, so pop pc is safe.
 pop {r1, pc}
# 311 "/source/libgcc/config/arm/lib1funcs.S"
.endm
# 327 "/source/libgcc/config/arm/lib1funcs.S"
.macro FUNC_END name
 .size __\name, . - __\name
.endm

.macro DIV_FUNC_END name signed
 cfi_start __\name, .Lend_div0
.Ldiv0:

 THUMB_LDIV0 \name \signed



 cfi_end .Lend_div0
 FUNC_END \name
.endm

.macro THUMB_FUNC_START name
 .globl \name
 .type \name,function
 .thumb_func
\name:
.endm
# 366 "/source/libgcc/config/arm/lib1funcs.S"
.macro FUNC_START name
 .text
 .globl __\name
 .type __\name,function
 .align 0
 .force_thumb
 .thumb_func

__\name:
.endm

.macro ARM_SYM_START name
       .type \name,function
       .align 0
\name:
.endm

.macro SYM_END name
       .size \name, . - \name
.endm
# 441 "/source/libgcc/config/arm/lib1funcs.S"
.macro FUNC_ALIAS new old
 .globl __\new

 .thumb_set __\new, __\old



.endm
# 473 "/source/libgcc/config/arm/lib1funcs.S"
.macro WEAK name
 .weak __\name
.endm





work .req r4 @ XXXX is this safe ?
dividend .req r0
divisor .req r1
overdone .req r2
result .req r2
curbit .req r3
# 499 "/source/libgcc/config/arm/lib1funcs.S"
.macro ARM_DIV_BODY dividend, divisor, result, curbit
# 554 "/source/libgcc/config/arm/lib1funcs.S"
 @ Initially shift the divisor left 3 bits if possible,
 @ set curbit accordingly. This allows for curbit to be located
 @ at the left end of each 4-bit nibbles in the division loop
 @ to save one loop in most cases.
 tst \divisor, #0xe0000000
 moveq \divisor, \divisor, lsl #3
 moveq \curbit, #8
 movne \curbit, #1

 @ Unless the divisor is very big, shift it up in multiples of
 @ four bits, since this is the amount of unwinding in the main
 @ division loop. Continue shifting until the divisor is
 @ larger than the dividend.
1: cmp \divisor, #0x10000000
 cmplo \divisor, \dividend
 movlo \divisor, \divisor, lsl #4
 movlo \curbit, \curbit, lsl #4
 blo 1b

 @ For very big divisors, we must shift it a bit at a time, or
 @ we will be in danger of overflowing.
1: cmp \divisor, #0x80000000
 cmplo \divisor, \dividend
 movlo \divisor, \divisor, lsl #1
 movlo \curbit, \curbit, lsl #1
 blo 1b

 mov \result, #0



 @ Division loop
1: cmp \dividend, \divisor
 do_it hs, t
 subhs \dividend, \dividend, \divisor
 orrhs \result, \result, \curbit
 cmp \dividend, \divisor, lsr #1
 do_it hs, t
 subhs \dividend, \dividend, \divisor, lsr #1
 orrhs \result, \result, \curbit, lsr #1
 cmp \dividend, \divisor, lsr #2
 do_it hs, t
 subhs \dividend, \dividend, \divisor, lsr #2
 orrhs \result, \result, \curbit, lsr #2
 cmp \dividend, \divisor, lsr #3
 do_it hs, t
 subhs \dividend, \dividend, \divisor, lsr #3
 orrhs \result, \result, \curbit, lsr #3
 cmp \dividend, #0 @ Early termination?
 do_it ne, t
 movnes \curbit, \curbit, lsr #4 @ No, any more bits to do?
 movne \divisor, \divisor, lsr #4
 bne 1b



.endm

.macro ARM_DIV2_ORDER divisor, order
# 621 "/source/libgcc/config/arm/lib1funcs.S"
 cmp \divisor, #(1 << 16)
 movhs \divisor, \divisor, lsr #16
 movhs \order, #16
 movlo \order, #0

 cmp \divisor, #(1 << 8)
 movhs \divisor, \divisor, lsr #8
 addhs \order, \order, #8

 cmp \divisor, #(1 << 4)
 movhs \divisor, \divisor, lsr #4
 addhs \order, \order, #4

 cmp \divisor, #(1 << 2)
 addhi \order, \order, #3
 addls \order, \order, \divisor, lsr #1



.endm

.macro ARM_MOD_BODY dividend, divisor, order, spare
# 669 "/source/libgcc/config/arm/lib1funcs.S"
 mov \order, #0

 @ Unless the divisor is very big, shift it up in multiples of
 @ four bits, since this is the amount of unwinding in the main
 @ division loop. Continue shifting until the divisor is
 @ larger than the dividend.
1: cmp \divisor, #0x10000000
 cmplo \divisor, \dividend
 movlo \divisor, \divisor, lsl #4
 addlo \order, \order, #4
 blo 1b

 @ For very big divisors, we must shift it a bit at a time, or
 @ we will be in danger of overflowing.
1: cmp \divisor, #0x80000000
 cmplo \divisor, \dividend
 movlo \divisor, \divisor, lsl #1
 addlo \order, \order, #1
 blo 1b



 @ Perform all needed substractions to keep only the reminder.
 @ Do comparisons in batch of 4 first.
 subs \order, \order, #3 @ yes, 3 is intended here
 blt 2f

1: cmp \dividend, \divisor
 subhs \dividend, \dividend, \divisor
 cmp \dividend, \divisor, lsr #1
 subhs \dividend, \dividend, \divisor, lsr #1
 cmp \dividend, \divisor, lsr #2
 subhs \dividend, \dividend, \divisor, lsr #2
 cmp \dividend, \divisor, lsr #3
 subhs \dividend, \dividend, \divisor, lsr #3
 cmp \dividend, #1
 mov \divisor, \divisor, lsr #4
 subges \order, \order, #4
 bge 1b

 tst \order, #3
 teqne \dividend, #0
 beq 5f

 @ Either 1, 2 or 3 comparison/substractions are left.
2: cmn \order, #2
 blt 4f
 beq 3f
 cmp \dividend, \divisor
 subhs \dividend, \dividend, \divisor
 mov \divisor, \divisor, lsr #1
3: cmp \dividend, \divisor
 subhs \dividend, \dividend, \divisor
 mov \divisor, \divisor, lsr #1
4: cmp \dividend, \divisor
 subhs \dividend, \dividend, \divisor
5:



.endm

.macro THUMB_DIV_MOD_BODY modulo
 @ Load the constant 0x10000000 into our work register.
 movs work, #1
 lsls work, #28
.Loop1:
 @ Unless the divisor is very big, shift it up in multiples of
 @ four bits, since this is the amount of unwinding in the main
 @ division loop. Continue shifting until the divisor is
 @ larger than the dividend.
 cmp divisor, work
 bhs .Lbignum
 cmp divisor, dividend
 bhs .Lbignum
 lsls divisor, #4
 lsls curbit, #4
 b .Loop1
.Lbignum:
 @ Set work to 0x80000000
 lsls work, #3
.Loop2:
 @ For very big divisors, we must shift it a bit at a time, or
 @ we will be in danger of overflowing.
 cmp divisor, work
 bhs .Loop3
 cmp divisor, dividend
 bhs .Loop3
 lsls divisor, #1
 lsls curbit, #1
 b .Loop2
.Loop3:
 @ Test for possible subtractions ...
  .if \modulo
 @ ... On the final pass, this may subtract too much from the dividend,
 @ so keep track of which subtractions are done, we can fix them up
 @ afterwards.
 movs overdone, #0
 cmp dividend, divisor
 blo .Lover1
 subs dividend, dividend, divisor
.Lover1:
 lsrs work, divisor, #1
 cmp dividend, work
 blo .Lover2
 subs dividend, dividend, work
 mov ip, curbit
 movs work, #1
 rors curbit, work
 orrs overdone, curbit
 mov curbit, ip
.Lover2:
 lsrs work, divisor, #2
 cmp dividend, work
 blo .Lover3
 subs dividend, dividend, work
 mov ip, curbit
 movs work, #2
 rors curbit, work
 orrs overdone, curbit
 mov curbit, ip
.Lover3:
 lsrs work, divisor, #3
 cmp dividend, work
 blo .Lover4
 subs dividend, dividend, work
 mov ip, curbit
 movs work, #3
 rors curbit, work
 orrs overdone, curbit
 mov curbit, ip
.Lover4:
 mov ip, curbit
  .else
 @ ... and note which bits are done in the result. On the final pass,
 @ this may subtract too much from the dividend, but the result will be ok,
 @ since the "bit" will have been shifted out at the bottom.
 cmp dividend, divisor
 blo .Lover1
 subs dividend, dividend, divisor
 orrs result, result, curbit
.Lover1:
 lsrs work, divisor, #1
 cmp dividend, work
 blo .Lover2
 subs dividend, dividend, work
 lsrs work, curbit, #1
 orrs result, work
.Lover2:
 lsrs work, divisor, #2
 cmp dividend, work
 blo .Lover3
 subs dividend, dividend, work
 lsrs work, curbit, #2
 orrs result, work
.Lover3:
 lsrs work, divisor, #3
 cmp dividend, work
 blo .Lover4
 subs dividend, dividend, work
 lsrs work, curbit, #3
 orrs result, work
.Lover4:
  .endif

 cmp dividend, #0 @ Early termination?
 beq .Lover5
 lsrs curbit, #4 @ No, any more bits to do?
 beq .Lover5
 lsrs divisor, #4
 b .Loop3
.Lover5:
  .if \modulo
 @ Any subtractions that we should not have done will be recorded in
 @ the top three bits of "overdone". Exactly which were not needed
 @ are governed by the position of the bit, stored in ip.
 movs work, #0xe
 lsls work, #28
 ands overdone, work
 beq .Lgot_result

 @ If we terminated early, because dividend became zero, then the
 @ bit in ip will not be in the bottom nibble, and we should not
 @ perform the additions below. We must test for this though
 @ (rather relying upon the TSTs to prevent the additions) since
 @ the bit in ip could be in the top two bits which might then match
 @ with one of the smaller RORs.
 mov curbit, ip
 movs work, #0x7
 tst curbit, work
 beq .Lgot_result

 mov curbit, ip
 movs work, #3
 rors curbit, work
 tst overdone, curbit
 beq .Lover6
 lsrs work, divisor, #3
 adds dividend, work
.Lover6:
 mov curbit, ip
 movs work, #2
 rors curbit, work
 tst overdone, curbit
 beq .Lover7
 lsrs work, divisor, #2
 adds dividend, work
.Lover7:
 mov curbit, ip
 movs work, #1
 rors curbit, work
 tst overdone, curbit
 beq .Lgot_result
 lsrs work, divisor, #1
 adds dividend, work
  .endif
.Lgot_result:
.endm





.macro BranchToDiv n, label
 lsrs curbit, dividend, \n
 cmp curbit, divisor
 blo \label
.endm



.macro DoDiv n
 lsrs curbit, dividend, \n
 cmp curbit, divisor
 bcc 1f
 lsls curbit, divisor, \n
 subs dividend, dividend, curbit

1: adcs result, result
.endm





.macro THUMB1_Div_Positive
 movs result, #0
 BranchToDiv #1, .Lthumb1_div1
 BranchToDiv #4, .Lthumb1_div4
 BranchToDiv #8, .Lthumb1_div8
 BranchToDiv #12, .Lthumb1_div12
 BranchToDiv #16, .Lthumb1_div16
.Lthumb1_div_large_positive:
 movs result, #0xff
 lsls divisor, divisor, #8
 rev result, result
 lsrs curbit, dividend, #16
 cmp curbit, divisor
 blo 1f
 asrs result, #8
 lsls divisor, divisor, #8
 beq .Ldivbyzero_waypoint

1: lsrs curbit, dividend, #12
 cmp curbit, divisor
 blo .Lthumb1_div12
 b .Lthumb1_div16
.Lthumb1_div_loop:
 lsrs divisor, divisor, #8
.Lthumb1_div16:
 Dodiv #15
 Dodiv #14
 Dodiv #13
 Dodiv #12
.Lthumb1_div12:
 Dodiv #11
 Dodiv #10
 Dodiv #9
 Dodiv #8
 bcs .Lthumb1_div_loop
.Lthumb1_div8:
 Dodiv #7
 Dodiv #6
 Dodiv #5
.Lthumb1_div5:
 Dodiv #4
.Lthumb1_div4:
 Dodiv #3
.Lthumb1_div3:
 Dodiv #2
.Lthumb1_div2:
 Dodiv #1
.Lthumb1_div1:
 subs divisor, dividend, divisor
 bcs 1f
 cpy divisor, dividend

1: adcs result, result
 cpy dividend, result
 bx lr

.Ldivbyzero_waypoint:
 b .Ldiv0
.endm




.macro THUMB1_Div_Negative
 lsrs result, divisor, #31
 beq 1f
 negs divisor, divisor

1: asrs curbit, dividend, #32
 bcc 2f
 negs dividend, dividend

2: eors curbit, result
 movs result, #0
 cpy ip, curbit
 BranchToDiv #4, .Lthumb1_div_negative4
 BranchToDiv #8, .Lthumb1_div_negative8
.Lthumb1_div_large:
 movs result, #0xfc
 lsls divisor, divisor, #6
 rev result, result
 lsrs curbit, dividend, #8
 cmp curbit, divisor
 blo .Lthumb1_div_negative8

 lsls divisor, divisor, #6
 asrs result, result, #6
 cmp curbit, divisor
 blo .Lthumb1_div_negative8

 lsls divisor, divisor, #6
 asrs result, result, #6
 cmp curbit, divisor
 blo .Lthumb1_div_negative8

 lsls divisor, divisor, #6
 beq .Ldivbyzero_negative
 asrs result, result, #6
 b .Lthumb1_div_negative8
.Lthumb1_div_negative_loop:
 lsrs divisor, divisor, #6
.Lthumb1_div_negative8:
 DoDiv #7
 DoDiv #6
 DoDiv #5
 DoDiv #4
.Lthumb1_div_negative4:
 DoDiv #3
 DoDiv #2
 bcs .Lthumb1_div_negative_loop
 DoDiv #1
 subs divisor, dividend, divisor
 bcs 1f
 cpy divisor, dividend

1: cpy curbit, ip
 adcs result, result
 asrs curbit, curbit, #1
 cpy dividend, result
 bcc 2f
 negs dividend, dividend
 cmp curbit, #0

2: bpl 3f
 negs divisor, divisor

3: bx lr

.Ldivbyzero_negative:
 cpy curbit, ip
 asrs curbit, curbit, #1
 bcc .Ldiv0
 negs dividend, dividend
.endm
# 1462 "/source/libgcc/config/arm/lib1funcs.S"
 WEAK aeabi_idiv0
 WEAK aeabi_ldiv0
 FUNC_START aeabi_idiv0
 FUNC_START aeabi_ldiv0
 bx lr
 FUNC_END aeabi_ldiv0
 FUNC_END aeabi_idiv0
# 2245 "/source/libgcc/config/arm/lib1funcs.S"
.macro CFI_START_FUNCTION
 .cfi_startproc
 .cfi_remember_state
.endm

.macro CFI_END_FUNCTION
 .cfi_restore_state
 .cfi_endproc
.endm
# 2263 "/source/libgcc/config/arm/lib1funcs.S"
# 1 "/source/libgcc/config/arm/bpabi-v6m.S" 1
# 33 "/source/libgcc/config/arm/bpabi-v6m.S"
 .eabi_attribute 25, 1
# 83 "/source/libgcc/config/arm/bpabi-v6m.S"
.macro test_div_by_zero signed
 cmp r3, #0
 bne 7f
 cmp r2, #0
 bne 7f
 cmp r1, #0
 .ifc \signed, unsigned
 bne 2f
 cmp r0, #0
2:
 beq 3f
 movs r1, #0
 mvns r1, r1 @ 0xffffffff
 movs r0, r1
3:
 .else
 blt 6f
 bgt 4f
 cmp r0, #0
 beq 5f
4: movs r0, #0
 mvns r0, r0 @ 0xffffffff
 lsrs r1, r0, #1 @ 0x7fffffff
 b 5f
6: movs r1, #0x80
 lsls r1, r1, #24 @ 0x80000000
 movs r0, #0
5:
 .endif
 @ tailcalls are tricky on v6-m.
 push {r0, r1, r2}
 ldr r0, 1f
 adr r1, 1f
 adds r0, r1
 str r0, [sp, #8]
 @ We know we are not on armv4t, so pop pc is safe.
 pop {r0, r1, pc}
 .align 2
1:
 .word __aeabi_ldiv0 - 1b
7:
.endm
# 2264 "/source/libgcc/config/arm/lib1funcs.S" 2
