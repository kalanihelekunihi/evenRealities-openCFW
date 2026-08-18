/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room Thumb-2 recreation of the IAR DLIB scanf %[...] scanset
 * membership matcher identified in the official Even Realities G2 2.2.6.10
 * Apollo-main image (stock body [0x004D2112,0x004D2158), 70 bytes), bounded
 * by the formatted-I/O audit in docs/research/g2-iar-dlib-format-io-recovery.md
 * (Unicorn-qualified: 4,022 stock verdicts reproduced).
 *
 * The leaf interprets a compiled scanset table as a byte stream of two entry
 * kinds, walking it with a remaining-byte countdown, and returns 1 on
 * membership / 0 on table exhaustion:
 *
 *   - range triple: any window of three-or-more remaining bytes whose second
 *     byte is '-' (0x2D) matches when table[0] <= ch <= table[2]; a non-match
 *     consumes three bytes; and
 *   - literal entry: any other byte matches when it equals ch and consumes
 *     one byte.
 *
 * A trailing window of fewer than three bytes is matched as literals only,
 * so a trailing '-' can never open a range.  The character is masked to eight
 * bits (stock UXTB).  The leaf performs no calls, no literal-pool loads, and
 * no writes.
 *
 * The recovered stock leaf is IAR DLIB Thumb-2 assembly whose predicated form
 * (ITT/IT blocks, r12 scratch, frameless caller-saved-only allocation, and
 * the two disjoint return sites) is not reproducible from portable C by the
 * reviewed apple-clang toolchain; like the frexpf/ldexpf, math-errno, and
 * memcpy/memmove siblings in this IAR-DLIB cluster it is therefore expressed
 * as a sectionized, Clang-syntax source recreation of the audit's recovered
 * control flow.  No IAR source or object bytes are imported.
 *
 * ABI (recovered): r0 = compiled scanset table, r1 = candidate character,
 * r2 = remaining table bytes; result in r0.
 */

    .syntax unified
    .cpu cortex-m55
    .thumb

    .section .text.open_cfw_iar_scanset_match, "ax", %progbits
    .p2align 1
    .global open_cfw_iar_scanset_match
    .type open_cfw_iar_scanset_match, %function
    .thumb_func
open_cfw_iar_scanset_match:
    uxtb    r1, r1                  @ value = ch & 0xFF
    b       .Lcond
.Lrange:
    ldrb    r3, [r0]                @ table[0]
    cmp     r1, r3                  @ value >= table[0] ?
    itt     ge
    ldrbge  r12, [r0, #2]           @ table[2]
    cmpge   r12, r1                 @ table[2] >= value ?
    bge     .Lret1                  @ membership: lo <= value <= hi
    adds    r0, r0, #3              @ cursor += 3
    subs    r2, r2, #3              @ remaining -= 3
.Lcond:
    cmp     r2, #3
    blo     .Ltail                  @ fewer than 3 remaining -> literal tail
    ldrb    r3, [r0, #1]            @ cursor[1]
    cmp     r3, #0x2d               @ '-' opens a range triple
    beq     .Lrange
    ldrb    r12, [r0], #1           @ literal entry: *cursor++
    cmp     r12, r1
    it      ne
    subne   r2, r2, #1              @ non-match consumes one byte
    bne     .Lcond
    b       .Lret1                  @ literal match
.Ltail:
    cbz     r2, .Lret0              @ table exhausted
.Ltloop:
    ldrb    r3, [r0], #1            @ *cursor++
    cmp     r3, r1
    beq     .Lret1
    subs    r2, r2, #1
    bne     .Ltloop
    b       .Lret0
.Lret1:
    movs    r0, #1
    bx      lr
.Lret0:
    movs    r0, #0
    bx      lr
    .size open_cfw_iar_scanset_match, . - open_cfw_iar_scanset_match
