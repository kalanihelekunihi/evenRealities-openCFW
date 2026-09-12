/* SPDX-License-Identifier: MIT */
/* Reviewed UART-configure leaf for the GX8002 UART boot stage 1
 * (IRAM) image: runtime 0x10000C9C, package 0xCEC, 208 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior of the
 * UART register-configure block: when the entry descriptor word is
 * nonzero, program the seven 0xA0005000-block control registers
 * (0x1C/0x20/0x24/0x28/0x2C/0x30 plus the 0x3C enable triple) from the
 * entry descriptor words by read-modify-write, then chain into the
 * retained rail-configure flow at 0x1000046C (a genuine external
 * boundary, same precedent as the reviewed mdelay leaf's chain into
 * that same address). The routine never returns.
 *
 * Assembly (rather than C) because the body is dense hand-scheduled
 * 16-bit read-modify-write traffic (two-byte ld.w/st.w/bclri/andi
 * throughout) with an inline literal pool: GCC -Os materializes the
 * MMIO base through its own end-of-section pool, which cannot sit
 * inline as in stock, and respells the mask sequences less densely.
 * No SDK text is reproduced and no SDK register map is used: the
 * 0xA0005000 base and every offset, mask, and bit position below is a
 * numeric immediate observed in the decoded stock flow. The pinned
 * upstream SDK checkout is not a build input to this leaf.
 *
 * Two reviewed-form deviations from stock (both battery-proven):
 *
 * - The stock `lrw r3, [pool]` for the 0xA0005000 base (2 bytes, pool
 *   word at package 0xDE0 inside the retained dead tail past the
 *   chaining branch) is materialized with movih/ori: the assembler
 *   places literal pools only at the section end, so an `lrw` pool
 *   cannot sit inline as in stock (same precedent as the reviewed
 *   pmudispatch leaf's retained-table bases).
 * - The stock frame is dropped and the dead entry move is gone:
 *   the body never reads r4-r6 (the entry `mov r4, r1` writes a
 *   register nothing observes) and uses no stack slot, so `push
 *   r4-r6, r15`, the zero-path `pop r4-r6, r15`, and the dead move
 *   are omitted and the leaf chains without restoring. Stock r4 at
 *   the chain therefore holds entry r1 while the reviewed form holds
 *   the passthrough seed; r4 is implementation-defined there and is
 *   dead downstream (retained 0x1000046C saves r4/r5 in its first
 *   instruction before any read). The stack-window traffic the
 *   dropped frame removes is excluded from trace comparison (same
 *   precedent as the reviewed mdelay leaf's window exclusion); the
 *   battery aligns the source entry sp per path so the link register
 *   state at the chaining branch matches exactly.
 *
 * Behavior summary (see the audit doc for the full decode): r3 =
 * [r0]; when zero, set r0 = 0 (the body runs either way). Clear bits
 * 1 then 0 of the 0x3C register. r2 = [r0]; when zero, chain. Else:
 * clear bit 6 of 0x1C and OR in [r0+0x10]; clear bits 8/5 of 0x20 and
 * OR in the byte at [r0+0x14]; take bits 8..12 of [r0+0x14] (zext
 * 12,8) and OR into 0x24; clear bit 3 of 0x28 and OR in [r0+0x24];
 * clear bit 7 of 0x2C and OR in [r0+0x18]; clear bit 3 of 0x30, OR in
 * ([r0+0x2C] & 7), clear bits 5/4, OR in ([r0+0x20] << 4); clear bit 2
 * of 0x3C, OR in (([r0+0x1C] << 2) & 4); set bits 1 then 0 of 0x3C;
 * chain into retained 0x1000046C.
 *
 * The sequence below is verified by decoded-target execution
 * comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-uartcfg-source.md), not by byte
 * identity, though the transliteration keeps the stock register plan
 * so the comparison is instruction-for-instruction.
 */
.section .text.open_cfw_gx8002_uart_stage1_uart_config,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_uart_config
.type open_cfw_gx8002_uart_stage1_uart_config,@function
open_cfw_gx8002_uart_stage1_uart_config:
    /* Entry (stock 0xC9C). No push: the body never touches r4-r6 or
     * any stack slot (see header note); entry r1/r4-r6 are dead and
     * pass through untouched on both sides. */
    ld.w r3, (r0, 0x0)
    bnez r3, .Lbody
    movi r0, 0
    /* No pop on the zero path (frameless; stock pops its pushed frame
     * here and re-executes the body with r0 = 0 either way). */
.Lbody:
    /* MMIO base (stock 0xCAA): stock loads 0xA0005000 through the
     * inline pool word at package 0xDE0 (retained dead tail); the
     * reviewed form materializes it with movih/ori. */
    movih r3, 0xA000
    ori r3, r3, 0x5000
    /* Enable triple, bits 1 then 0 of 0x3C (stock 0xCAC). */
    ld.w r2, (r3, 0x3c)
    bclri r2, 1
    st.w r2, (r3, 0x3c)
    ld.w r2, (r3, 0x3c)
    bclri r2, 0
    st.w r2, (r3, 0x3c)
    /* Descriptor gate (stock 0xCB8): a zero descriptor word chains
     * with no register programming. */
    ld.w r2, (r0, 0x0)
    bez r2, .Lchain
    /* 0x1C: clear bit 6, OR in [r0+0x10] (stock 0xCBE). */
    movi r1, 0
    ld.w r2, (r3, 0x1c)
    subi r1, 64
    and r2, r1
    st.w r2, (r3, 0x1c)
    ld.w r2, (r3, 0x1c)
    ld.w r1, (r0, 0x10)
    or r2, r1
    st.w r2, (r3, 0x1c)
    /* 0x20: clear bits 8 and 5, OR in the byte at [r0+0x14]
     * (stock 0xCD0). */
    movi r1, 0
    ld.w r2, (r3, 0x20)
    subi r1, 256
    and r2, r1
    st.w r2, (r3, 0x20)
    movi r1, 0
    ld.w r2, (r3, 0x24)
    subi r1, 32
    and r2, r1
    st.w r2, (r3, 0x24)
    ld.w r1, (r3, 0x20)
    ld.b r2, (r0, 0x14)
    or r2, r1
    st.w r2, (r3, 0x20)
    /* 0x24: OR in bits 8..12 of [r0+0x14] (stock 0xCEC). */
    ld.w r2, (r0, 0x14)
    ld.w r1, (r3, 0x24)
    zext r2, r2, 12, 8
    or r2, r1
    st.w r2, (r3, 0x24)
    /* 0x28: clear bit 3, OR in [r0+0x24] (stock 0xCF8). */
    movi r1, 0
    ld.w r2, (r3, 0x28)
    subi r1, 8
    and r2, r1
    st.w r2, (r3, 0x28)
    ld.w r2, (r3, 0x28)
    ld.w r1, (r0, 0x24)
    or r2, r1
    st.w r2, (r3, 0x28)
    /* 0x2C: clear bit 7, OR in [r0+0x18] (stock 0xD0A). */
    movi r1, 0
    ld.w r2, (r3, 0x2c)
    subi r1, 128
    and r2, r1
    st.w r2, (r3, 0x2c)
    ld.w r2, (r3, 0x2c)
    ld.w r1, (r0, 0x18)
    or r2, r1
    st.w r2, (r3, 0x2c)
    /* 0x30: clear bit 3, OR in ([r0+0x2C] & 7), clear bits 5 and 4,
     * OR in ([r0+0x20] << 4) (stock 0xD1C). */
    movi r1, 0
    ld.w r2, (r3, 0x30)
    subi r1, 8
    and r2, r1
    st.w r2, (r3, 0x30)
    ld.w r2, (r0, 0x2c)
    ld.w r1, (r3, 0x30)
    andi r2, r2, 7
    or r2, r1
    st.w r2, (r3, 0x30)
    ld.w r2, (r3, 0x30)
    bclri r2, 4
    bclri r2, 5
    st.w r2, (r3, 0x30)
    ld.w r1, (r3, 0x30)
    ld.w r2, (r0, 0x20)
    lsli r2, r2, 4
    or r2, r1
    st.w r2, (r3, 0x30)
    /* 0x3C: clear bit 2, OR in (([r0+0x1C] << 2) & 4), set bits 1
     * then 0 (stock 0xD44). */
    ld.w r2, (r3, 0x3c)
    bclri r2, 2
    st.w r2, (r3, 0x3c)
    ld.w r2, (r0, 0x1c)
    lsli r2, r2, 2
    ld.w r1, (r3, 0x3c)
    andi r2, r2, 4
    or r2, r1
    st.w r2, (r3, 0x3c)
    ld.w r2, (r3, 0x3c)
    ori r2, r2, 2
    st.w r2, (r3, 0x3c)
    ld.w r2, (r3, 0x3c)
    ori r2, r2, 1
    st.w r2, (r3, 0x3c)
.Lchain:
    /* Chain into the retained rail-configure flow (stock 0xD68). The
     * target is a linker-assigned absolute symbol, not a relocation
     * (mdelay-leaf precedent); the routine never returns. */
    bsr open_cfw_gx8002_uart_boot_stage1_46c_entry
