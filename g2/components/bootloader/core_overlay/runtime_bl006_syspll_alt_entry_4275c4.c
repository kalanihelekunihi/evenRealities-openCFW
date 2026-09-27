/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the dead System-PLL alternate
 * setter entry at 0x004275C4..0x004275D2 (14 B).
 *
 * The stock image holds two adjacent setter prologues that share
 * the publish body at 0x004275DE (already routed as part of the
 * `open_cfw_bootloader_double_range_error_4275d2` leaf span):
 * the routed entry at 0x004275D2 publishes 0x22, while this
 * alternate entry publishes 0x21. Registers on entry: none live;
 * the entry builds its own frame, loads the range-error status
 * cell pointer from the literal word at 0x004275E4 (the named
 * layout word reproduced in runtime_bl006_syspll_pool_427588.c,
 * value 0x20027194), selects 0x21, and transfers into the shared
 * body:
 *   push {r0-r3, lr}; sub sp, #4; r0 = 0
 *   r1 = *(0x004275E4); r2 = 0x21; goto 0x004275DE
 *
 * The branch is expressed as a reviewed narrow Thumb relocation
 * (`R_ARM_THM_JUMP11`) against an undefined fixed-address join
 * symbol.  The in-place extractor binds that symbol to 0x004275DE
 * and materializes the same 16-bit branch as stock, without a raw
 * instruction transcript in this source file.
 *
 * The span sits in the System-PLL region the whole-image retained
 * survey grades corroborated_unreachable_control_flow; its known
 * inbound references are the replaced double-ldexp wrapper/core
 * spans and the binary32 remainder tail admitted in this same
 * turn (whose `blo.w` lands here), all dead in the built image. A
 * whole-image `bl` sweep finds no caller of this entry. The
 * reconstruction documents the bytes from reviewed source and
 * pins the behavior the replaced heads must cover; no live
 * traffic is claimed. See
 * docs/research/g2-bootloader-bl006-tail-leaves-426c22-427d84-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_se_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_SE_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_SE_ATTR __attribute__((used, noinline))
#endif

/* Alternate setter entry: publish selector 0x21 to the
 * range-error status cell, then join the shared body. */
OPEN_CFW_BL006_SE_ATTR
open_cfw_bl006_se_u32 open_cfw_bootloader_syspll_alt_entry_4275c4(
    open_cfw_bl006_se_u32 cell_value,
    open_cfw_bl006_se_u32 *selector_out)
{
#if defined(__arm__) || defined(__thumb__)
    /* The join branch `b #0x004275DE` targets outside this
     * section.  A plain external `b` widens to a 24-bit relocation,
     * so use a reviewed 11-bit Thumb branch relocation at the exact
     * branch halfword.  The extraction contract verifies the global
     * undefined STT_NOTYPE symbol and fixed target address before
     * materializing the stock `05 e0` branch. */
    __asm__ volatile(
        "push {r0, r1, r2, r3, lr}\n"
        "sub sp, #4\n"
        "movs r0, #0\n"
        "mov r8, r8\n"
        "ldr r1, [pc, #0x14]\n"
        "movs r2, #0x21\n"
        ".reloc ., R_ARM_THM_JUMP11, open_cfw_bootloader_double_range_error_4275d2_join\n"
        "b.n .\n");
#else
    /* Host twin: the stock entry loads the cell pointer from the
     * literal word (taken explicitly here) and selects 0x21. The
     * join branch into the shared publish body is pinned by the
     * byte-exact rebuild, not by host execution. */
    *selector_out = 0x21U;
    return cell_value;
#endif
}
