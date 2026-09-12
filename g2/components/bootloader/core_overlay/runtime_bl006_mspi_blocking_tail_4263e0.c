/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of one dead G2 bootloader interior:
 *
 *  N. MSPI blocking-transfer remainder at 0x004263E0..0x0042644C
 *     (108 B; the survey region extends 4 bytes further to
 *     0x00426450, but 0x0042644C is already covered by the
 *     source-owned alignment word `bl006_word_42644c`), the
 *     surviving end of the replaced stock blocking-transfer
 *     service (live replacement: the source-owned
 *     blocking-transfer body that returns before this span).
 *     Single entry (fallthrough from the replaced head at
 *     0x004263DE); registers on entry are head-owned
 *     (r1 = transfer descriptor, r4 = device index, r5 = MSPI
 *     base, r6/r7 = saved words, r8/ip = tables):
 *       mode = [r1 + 6]
 *       mode == 0: r0 = fifo_read(r4, [r1], [r1 + 0x14])
 *       mode == 1: r0 = fifo_write(r4, [r1], [r1 + 0x14])
 *       other:     r0 passes through from the head
 *       if (r0 != 0): restore r7 -> [base + 0x208],
 *         r6 -> [base + 0x200]; return r0
 *       else: r0 = delay_service(...); restore the same two
 *         words; return r0
 *     with base = r5 + (r4 << 12). Single exit through
 *     `pop.w {r1, r2, r4-r8, pc}`.
 *
 * Calls: the FIFO-read/write calls target the source-owned
 * in-place services `open_cfw_bootloader_mspi_fifo_read_423e8a`
 * and `open_cfw_bootloader_mspi_fifo_write_423e40`, named as
 * reviewed R_ARM_THM_CALL relocations (bitmap-client precedent).
 * The delay-service call targets 0x0041D246, which stays retained
 * under another work item and has no source symbol; the
 * relocatable object cannot name it, so the instruction is
 * spelled with its reviewed 32-bit encoding (`.inst.w`,
 * binary32-tail precedent). The probe below proves the reference
 * assembler emits the identical bytes for an identical `bl` at
 * the identical offset (-37362).
 *
 * This leaf covers 0x004263E0..0x0042644C (108 B, closing
 * with the 4-byte `pop.w` at 0x00426448) and stops where the
 * already-covered alignment word begins.
 *
 * The whole-image survey grades the span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of the entry, so the leaf never executes
 * in the shipped image; the reconstruction documents the bytes
 * and pins the behavior the replaced head must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-4248e2-4263e0-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_bt_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_BT_ATTR __attribute__((used, naked, noinline))
extern open_cfw_bl006_bt_u32 open_cfw_bootloader_mspi_fifo_read_423e8a(
    open_cfw_bl006_bt_u32, open_cfw_bl006_bt_u32, open_cfw_bl006_bt_u32);
extern open_cfw_bl006_bt_u32 open_cfw_bootloader_mspi_fifo_write_423e40(
    open_cfw_bl006_bt_u32, open_cfw_bl006_bt_u32, open_cfw_bl006_bt_u32);
#else
#define OPEN_CFW_BL006_BT_ATTR __attribute__((used, noinline))
#endif

/* Leaf N: blocking-transfer remainder (108 B). */
OPEN_CFW_BL006_BT_ATTR
open_cfw_bl006_bt_u32 open_cfw_bootloader_mspi_blocking_rem_tail_4263e0(
    open_cfw_bl006_bt_u32 *window,
    open_cfw_bl006_bt_u32 base_off,
    open_cfw_bl006_bt_u32 index,
    open_cfw_bl006_bt_u32 mode,
    open_cfw_bl006_bt_u32 r0_in,
    open_cfw_bl006_bt_u32 fifo_result,
    open_cfw_bl006_bt_u32 delay_result,
    open_cfw_bl006_bt_u32 r6_in,
    open_cfw_bl006_bt_u32 r7_in)
{
#if defined(__arm__) || defined(__thumb__)
    /* Delay call at 0x00426434 targets retained 0x0041D246
     * (PC 0x00426438, offset -37362, stock bytes
     * f6 f7 07 ff). `.inst.w` takes the opcode halves in
     * reading order (first halfword high), so the spelling is
     * 0xF7F6FF07 for stock bytes f6 f7 07 ff. */
    __asm__ volatile(
        "adds r2, #4\n"
        "str.w lr, [r2]\n"
        "ldrb r2, [r1, #6]\n"
        "cmp r2, #0\n"
        "bne 0f\n"
        "ldr.w r3, [ip, #0x10]\n"
        "ldr r2, [r1]\n"
        "ldr r1, [r1, #0x14]\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_mspi_fifo_read_423e8a\n"
        "b 1f\n"
        "0: ldrb r2, [r1, #6]\n"
        "cmp r2, #1\n"
        "bne 1f\n"
        "ldr.w r3, [ip, #0x10]\n"
        "ldr r2, [r1]\n"
        "ldr r1, [r1, #0x14]\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_mspi_fifo_write_423e40\n"
        "1: cmp r0, #0\n"
        "beq 2f\n"
        "adds.w r1, r5, r4, lsl #12\n"
        "str.w r7, [r1, #0x208]\n"
        "adds.w r5, r5, r4, lsl #12\n"
        "str.w r6, [r5, #0x200]\n"
        "b 3f\n"
        "2: mov r0, r8\n"
        "movs r1, #1\n"
        "str r1, [sp]\n"
        "movs r3, #2\n"
        "movs r2, #2\n"
        "adds.w r1, r5, r4, lsl #12\n"
        ".inst.w 0xF7F6FF07\n"
        "adds.w r1, r5, r4, lsl #12\n"
        "str.w r7, [r1, #0x208]\n"
        "adds.w r5, r5, r4, lsl #12\n"
        "str.w r6, [r5, #0x200]\n"
        "3: pop.w {r1, r2, r4, r5, r6, r7, r8, pc}\n");
#else
    /* Host twin: the FIFO and delay results arrive explicitly
     * (target callees, one retained); the window models the
     * MSPI aperture as byte offsets. */
    open_cfw_bl006_bt_u32 r0;
    open_cfw_bl006_bt_u32 base = base_off + (index << 12U);
    if (mode == 0U || mode == 1U) {
        r0 = fifo_result;
    } else {
        r0 = r0_in;
    }
    if (r0 != 0U) {
        *(open_cfw_bl006_bt_u32 *)((unsigned char *)window + base + 0x208U) =
            r7_in;
        *(open_cfw_bl006_bt_u32 *)((unsigned char *)window + base + 0x200U) =
            r6_in;
        return r0;
    }
    r0 = delay_result;
    *(open_cfw_bl006_bt_u32 *)((unsigned char *)window + base + 0x208U) =
        r7_in;
    *(open_cfw_bl006_bt_u32 *)((unsigned char *)window + base + 0x200U) =
        r6_in;
    return r0;
#endif
}

#if defined(__arm__) || defined(__thumb__)
/* Assembler probe: identical `bl` at the identical offset
 * (-37362) proves the reviewed `.inst.w` spelling. The section
 * is discarded from the firmware image. */
OPEN_CFW_BL006_BT_ATTR
void open_cfw_bl006_bt_probe_bl_37362_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 37358\n"
        "bl 0b\n");
}
#endif
