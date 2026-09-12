/* SPDX-License-Identifier: MIT */
/* Reviewed second PMU dispatcher body for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x10000EB8, package 0xF08, 476 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * second PMU rail dispatcher from its restore block on: one
 * `pmu_fill_desc` call into a 24-byte stack descriptor, descriptor
 * byte/bit gating, a UART-clock divisor computation from the
 * 0xA0005000-block registers, and fill-retry loops that never return
 * (no `rts`; the routine is H-class, like the reviewed rail leaves).
 * The real linked fill body runs on the source side; the stock fill
 * runs on the stock side.
 *
 * The 24-byte entry head (runtime 0x10000EA0: frame setup, unsigned
 * id-range guard, retained jump-table dispatch through the inline
 * pool word at 0x10000EB4) stays retained stock and is NOT part of
 * this leaf. That head cannot be transliterated with this toolchain:
 * its jump-table targets are absolute retained addresses, so every
 * body arm must coincide with its stock address, while the
 * assembler's literal pools only sit at the section end (no
 * `.ltorg`), which would displace either the inline table pool or
 * the arms. Recording the measurements so followups do not repeat
 * them: an `lrw` head keeps arm addresses only with a 4-byte dead
 * pad beside its end pool (504 bytes total); a `movih`/`ori` head
 * costs 8 bytes against a 6-byte budget and its cross-section `bt`
 * to the body entry assembles to the 4-byte form; a bare numeric
 * `bt` operand misassembles silently and must never be used. Closing
 * the head needs assembler inline-pool support or an equivalent
 * toolchain change; it is a 24-byte followup, documented in the
 * audit doc.
 *
 * Assembly (rather than C) because the body dispatches through a
 * retained jump table and ends in an unreachable trap word: GCC cannot
 * emit layout tables of its own under the single-section-per-envelope
 * builder rule (pmudispatch precedent), and the dense hand-scheduled
 * 16-bit traffic transliterates exactly. No SDK text is reproduced and
 * no SDK register map is used: the 0xA0005000/0xA0010080 bases and
 * every offset, mask, and constant below is a numeric immediate
 * observed in the decoded stock flow. The pinned upstream SDK checkout
 * is not a build input to this leaf.
 *
 * The body entry at 0x10000EB8 is the retained table arm for ids
 * 7,8 and the fallthrough into the restore block; the retained
 * table arms for ids 9..25 land directly on the coinciding body
 * addresses below. Every branch in the body stays inside the body
 * past the entry pad, so all encodings match stock; the only
 * cross-reference is the linked fill call (pmudispatch precedent).
 *
 * Reviewed-form notes (all battery-proven):
 *
 * - Three-operand register shifts do not occur in this body (all
 *   shifts are two-operand or immediate), so the reversed-operand
 *   reading documented for the first dispatcher never triggers; the
 *   executor still implements it for shared-code parity.
 * - `mul.u32` writes its low 32 bits to the named destination; the
 *   body never reads the high half, so only the low word is modeled.
 * - Every `divu` site is provably nonzero on reachable paths (table-
 *   derived +1 floors and the `bez` guard); the executor fail-closes
 *   on a zero divisor and the battery excludes the one adversarial
 *   MMIO combination that could zero the 0xFDC divisor.
 * - The retained dispatch reads slot id-7 (stock 0xEAE `ldr.w r3,
 *   (r2, r3 << 2)`), so id 25 reads the last in-bounds slot (the
 *   0xF84 retry-10 arm), not past the table; all of ids 7..25 are
 *   covered by the battery and the table bounds are pinned against
 *   the stock dump.
 *
 * Behavior summary (see the audit doc for the full decode): restore
 * the frame (caller-stack words) and retry with fill id 19; on fill
 * failure repeat. On hit: b6 = signed entry byte 6; -1 ->
 * restore/retry-19. fill-id >= 10 -> the cell test; fill-id < 10
 * with (1<<id)&579 == 0 -> the cell test; else the extended bit
 * test. The cell test reads bit b6 of the entry word, then either
 * the divisor path (MMIO clock computation ending in divu +
 * restore/retry-16) or the bit-set path. The bit-set path runs the
 * 0xA001008C-gated clock arithmetic (mult/divu, range clamps) or the
 * entry-word multiplier path (mul.u32, shift/or fold), all joining
 * the descriptor-walk tail that ends in divu + restore/retry-16. The
 * 0xF28 region is a sink that always restores and retries 19. The
 * trailing `bkpt` is unreachable padding after an unconditional
 * branch.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-pmusecond-source.md), with
 * arm-address coincidence (not byte identity: two reviewed-form
 * deviations) as corroboration only.
 */
.section .text.open_cfw_gx8002_uart_stage1_pmu_second_body,"ax",@progbits
/* 2-byte alignment: the body entry 0x10000EBA is 2-mod-4 (envelope
 * offset 0xF0A), so a 4-byte balign would pad the entry. */
.balign 2
.global open_cfw_gx8002_uart_stage1_pmu_second_body
.type open_cfw_gx8002_uart_stage1_pmu_second_body,@function
open_cfw_gx8002_uart_stage1_pmu_second_body:
    /* Position pad (stock 0xEB8): the stock `movi r0, 0` writes a
     * register nothing observes before the next fill call
     * overwrites it, and the entry address is 4-aligned while the
     * dispatch tables demand coinciding arms. The reviewed form
     * keeps a 2-byte no-op here (assembles to `mov r0, r0`;
     * register-only, trace-neutral) so the restore block and every
     * later arm land at their stock addresses. */
    nop
    /* Restore-and-retry-19 (stock 0xEBA): also the fill-failure
     * target and the table arm for ids 7,8. */
.Lrestore19:
    addi r14, r14, 24
    pop r4, r15
    movi r4, 19
    /* Fill entry (stock 0xEC0): r0 = fill id, r1 = descriptor. */
.Lfill_entry:
    mov r1, r14
    mov r0, r4
    bsr open_cfw_gx8002_uart_stage1_pmu_fill_desc
    bnez r0, .Lrestore19
    /* Entry-byte gate (stock 0xECC): b6 == -1 restores/retries. */
    ld.w r1, (r14, 0x0)
    movi r3, 0
    ld.bs r2, (r1, 0x6)
    subi r3, 1
    cmpne r2, r3
    bf .Lrestore19
    /* Fill-id class (stock 0xEDA): >= 10 takes the cell test. */
    cmphsi r4, 10
    bt .Lcell_entry
    movi r3, 1
    lsl r3, r4
    andi r3, r3, 579
    bez r3, .Lcell_entry
    /* Extended bit test (stock 0xEEA). */
    movih r3, 40961
    bseti r3, 7
    addi r13, r2, 1
    ld.w r12, (r3, 0xc)
    ld.w r0, (r14, 0x8)
    bez r13, .Lbit_test
    ld.w r3, (r0, 0x0)
    lsr r3, r13
    andi r3, r3, 1
    bez r3, .Lbit_test
    movi r0, 32000
    br .Lwalk_entry
    /* Cell test entry (stock 0xF10). */
.Lcell_entry:
    movih r3, 40961
    bseti r3, 7
    ld.w r0, (r14, 0x8)
    ld.w r12, (r3, 0xc)
    /* Bit test (stock 0xF1C): bit b6 of the entry word. */
.Lbit_test:
    ld.w r3, (r0, 0x0)
    lsr r3, r2
    andi r3, r3, 1
    bnez r3, .Lbit_set
    /* Clock divisor select (stock 0xF28): a sink that always
     * restores and retries 19 (see header note). */
    movih r3, 4
    and r12, r3
    cmpnei r12, 0
    movi r3, 64000
    rotli r3, r3, 4
    movi r0, 48000
    rotli r0, r0, 8
    inct r0, r3, 0
    movi r3, 9
    cmphs r3, r4
    bf .Lrestore19
    cmpnei r4, 9
    bf .Lrestore19
    bclri r4, 2
    cmpnei r4, 2
    bf .Lrestore19
    /* Descriptor-walk tail (stock 0xF56): table-driven divisor. */
.Lwalk_entry:
    ld.w r12, (r14, 0x4)
.Lwalk_check:
    ld.w r2, (r1, 0x8)
    bez r2, .Lrestore19
    ld.b r3, (r2, 0x0)
    addu r3, r12
    ld.b r1, (r2, 0x1)
    ld.w r3, (r3, 0x0)
    lsr r3, r1
    ld.h r2, (r2, 0x2)
    and r3, r2
    bez r3, .Lrestore19
    addi r3, 1
    divu r0, r0, r3
    addi r14, r14, 24
    pop r4, r15
    /* Shared terminator (stock 0xF7C): the walk tail and the table
     * arm for ids 17,18 both retry with 16 here. */
.Lretry16:
    movi r4, 16
    br .Lfill_entry
    /* Table retry arms (stock 0xF80/0xF84). */
    movi r4, 22
    br .Lfill_entry
    movi r4, 10
    br .Lfill_entry
    /* Bit-set path (stock 0xF88). */
.Lbit_set:
    ld.w r0, (r0, 0x0)
    lsr r0, r2
    andi r0, r0, 1
    bez r0, .Lwalk_entry
    andi r12, r12, 1
    bez r12, .Lmul_path
    /* UART clock divisor computation (stock 0xF9C). */
    lrw r2, 0xa0005000
    movi r13, 7936
    ld.w r0, (r2, 0x1c)
    andi r0, r0, 63
    addi r12, r0, 1
    ld.w r0, (r2, 0x20)
    ld.w r3, (r2, 0x24)
    lsli r3, r3, 8
    and r3, r13
    ld.w r13, (r2, 0x28)
    ld.w r2, (r2, 0x30)
    zext r2, r2, 5, 4
    cmpnei r2, 2
    or r0, r3
    addi r3, r0, 1
    bf .Ldiv_cfg0
    cmpnei r2, 3
    bf .Ldiv_cfg1
    cmpnei r2, 1
    movi r0, 60000
    rotli r0, r0, 10
    movih r2, 1125
    inct r2, r0, 0
.Lclock_join:
    mult r2, r12
    movi r0, 15999
    nor r0, r0
    divu r2, r2, r3
    addu r18, r2, r0
    movi r0, 31999
    cmphs r0, r18
    bt .Ldiv_range0
    lrw r0, 0xfff83000
    addu r18, r2, r0
    lrw r0, 0x000f9fff
    cmphs r0, r18
    bt .Ldiv_range1
    lrw r0, 0xfffda800
    addu r2, r0
    lrw r0, 0x002c87ff
    cmphs r0, r2
    bt .Ldiv_range2
    movi r0, 0
    subi r0, 1
    br .Lrestore19
    /* Entry-word multiplier path (stock 0x1014). */
.Lmul_path:
    movih r0, 375
.Lmul_entry:
    ld.w r3, (r1, 0xc)
    ld.w r12, (r14, 0x4)
    bez r3, .Lwalk_check
    ld.b r3, (r3, 0x0)
    addu r3, r12
    ld.w r2, (r3, 0x0)
    movih r3, 2048
    and r3, r2
    bnez r3, .Lwalk_check
    zext r2, r2, 24, 0
    mul.u32 r2, r2, r0
    lsli r0, r3, 7
    /* GAS spelling for the stock `tlsri` (same encoding; the
     * disassembler prints the 32-bit-form alias). */
    lsri r2, r2, 25
    or r0, r2
    br .Lwalk_check
    /* Clamp arm (stock 0x1042): also joined from 0x105E/0x107C. */
.Ldiv_range0:
    movi r0, 32000
.Ldiv_range0_div:
    divu r0, r0, r12
    mult r0, r3
    andi r3, r13, 7
    addi r3, 1
    addu r3, r3
    divu r0, r0, r3
    br .Lmul_entry
.Ldiv_range1:
    movi r0, 64000
    rotli r0, r0, 4
    br .Ldiv_range0_div
.Ldiv_cfg1:
    movih r2, 1500
    br .Lclock_join
.Ldiv_cfg0:
    movi r2, 42000
    rotli r2, r2, 11
    br .Lclock_join
.Ldiv_range2:
    movi r0, 64000
    rotli r0, r0, 5
    br .Ldiv_range0_div
    /* Unreachable trap padding (stock 0x107E). Both forms never
     * execute there; the battery fail-closes on any visit. The
     * assembler-owned value pools for the five `lrw` sites follow
     * at the section end. */
    bkpt
