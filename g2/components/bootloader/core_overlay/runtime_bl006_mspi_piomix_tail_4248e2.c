/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of one dead G2 bootloader interior:
 *
 *  M. MSPI PIO-mixed configuration remainder at
 *     0x004248E2..0x00424976 (148 B), the surviving arms of the
 *     replaced stock PIO-mixed configuration service (live
 *     replacement: the source-owned MSPI PIO-mixed configuration
 *     body that returns before this span). Seven entries, all fed
 *     only from the replaced head; every arm rejoins the shared
 *     epilogue at 0x00424972 (`movs r0, #0; bx lr`):
 *       E0 at 0x004248E2: r0 = register block. Sets the low
 *         nibble at [r0 + 4] to 1:
 *           [r0 + 4] = ([r0 + 4] & ~0xF) | 1
 *       E1 at 0x004248F0: r1 = device index. Loads the MSPI base
 *         word from the retained pool at 0x004251A4 and sets the
 *         low nibble at [base + (r1 << 12) + 4] to 3.
 *       E2 at 0x00424906: same shape, nibble 5.
 *       E3 at 0x0042491C: same shape, nibble 7.
 *       E4 at 0x00424932: same shape but clears the low nibble
 *         (`lsrs`/`lsls` by 4); the pool word is read from
 *         0x004251A6 (halfword-shifted view of the same pool).
 *       E5 at 0x00424946: same shape, nibble 9.
 *       E6 at 0x0042495C: same shape, nibble 11.
 *     All six pool loads reuse the retained pool words through
 *     their stock PC-relative offsets (same precedent as the
 *     bitmap-client leaves, which name pool addresses only in
 *     comments); no relocation is involved.
 *
 * The whole-image survey grades the span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so no leaf executes in the
 * shipped image; the reconstruction documents the bytes and pins
 * the behavior the replaced head must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-4248e2-4263e0-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_pm_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_PM_ATTR __attribute__((used, naked, noinline))
#else
#define OPEN_CFW_BL006_PM_ATTR __attribute__((used, noinline))
#endif

/* Leaf M: PIO-mixed nibble arms plus shared epilogue (148 B). */
OPEN_CFW_BL006_PM_ATTR
open_cfw_bl006_pm_u32 open_cfw_bootloader_mspi_piomix_rem_tail_4248e2(
    open_cfw_bl006_pm_u32 *window,
    open_cfw_bl006_pm_u32 reg_block_off,
    open_cfw_bl006_pm_u32 pool_base_off,
    open_cfw_bl006_pm_u32 index,
    unsigned entry)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "adds r0, r0, #4\n"
        "movs r1, #1\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x8b0]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "movs r1, #3\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x89c]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "movs r1, #5\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x884]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "movs r1, #7\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x870]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #4\n"
        "lsls r1, r1, #4\n"
        "str r1, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x85c]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "movs r1, #9\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "ldr.w r0, [pc, #0x844]\n"
        "adds.w r0, r0, r1, lsl #12\n"
        "adds r0, r0, #4\n"
        "movs r1, #0xb\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #4\n"
        "str r2, [r0]\n"
        "b 0f\n"
        "0: movs r0, #0\n"
        "bx lr\n");
#else
    /* Host twin: the entry selector names the stock entry (0-6
     * for E0-E6). The window models target register memory as
     * byte offsets; the pool word arrives as an explicit offset
     * because the pool load is a target-address reuse, not host
     * memory. Nibbles per entry: 1, 3, 5, 7, clear, 9, 11. */
    static const open_cfw_bl006_pm_u32 nibbles[7] =
        {1U, 3U, 5U, 7U, 0x10U, 9U, 11U};
    open_cfw_bl006_pm_u32 off;
    open_cfw_bl006_pm_u32 *slot;
    if (entry == 0U) {
        off = reg_block_off + 4U;
    } else {
        off = pool_base_off + (index << 12U) + 4U;
    }
    slot = (open_cfw_bl006_pm_u32 *)((unsigned char *)window + off);
    if (nibbles[entry] == 0x10U) {
        *slot &= (open_cfw_bl006_pm_u32)~0xFU;
    } else {
        *slot = (*slot & (open_cfw_bl006_pm_u32)~0xFU) | nibbles[entry];
    }
    return 0U;
#endif
}
