/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of one dead G2 bootloader interior:
 *
 *  O. MSPI control-dispatcher remainder at 0x0042612C..0x004262E0
 *     (436 B), the surviving arms of the replaced stock MSPI
 *     control dispatcher (live replacement: the source-owned
 *     control dispatcher that returns before this span). Eight
 *     entries, all fed only from the replaced head; every arm
 *     rejoins a head join point (never returns):
 *       A0 at 0x0042612C: state counter++, primask publish; if
 *         r6 != 0, exit to the head (0x004260F4); r4 =
 *         cq_enable(r7); if r4 == 0, exit to the head; else
 *         exit E8 (0x004252E8) with r0 = r4.
 *       A1 at 0x00426152: descriptor validation (bytes 0/1);
 *         failure exits E8 with r0 = 6; success writes the
 *         bit-7/bit-5-6 fields at pool + 0x84 and exits E6
 *         (0x004252E6).
 *       A2 at 0x004261A2: if r2 == 0, exit E8 with r0 = 6,
 *         else run the A3 body.
 *       A3 at 0x004261AC: second-descriptor register
 *         configuration at pool + 0x84/0x90; exits E6.
 *       A4 at 0x004261EA: clears bit 6 at pool + 0x90; exits E6.
 *       A5 at 0x00426200: sets bit 6 at pool + 0x90; exits E6.
 *       A6 at 0x00426220: third-descriptor configuration at
 *         pool + 0xA4 (or the bit-0 clear path); exits E6.
 *       A7 at 0x004262DA: exits E8 with r0 = 6.
 *     E6 = 0x004252E6, E8 = 0x004252E8, both in the replaced
 *     head. The six pool loads reuse the retained pool word at
 *     0x00426804 through their stock PC-relative offsets
 *     (bitmap-client precedent; no relocation involved).
 *
 * Calls: the enable call targets the source-owned in-place
 * service `open_cfw_bootloader_mspi_cq_enable_423f8e`, named as
 * a reviewed R_ARM_THM_CALL relocation. All thirteen
 * out-of-span branches (two narrow conditionals, eleven wide)
 * are spelled with reviewed encodings (`.inst` / `.inst.w`,
 * binary32-tail precedent). The two narrow exits carry
 * in-source assembler probes proving the reference assembler
 * emits the identical bytes at the identical offsets; the
 * eleven wide exits are pinned instead by decoder verification
 * (the verifier disassembles each spelled site and checks the
 * branch target), because the reference assembler emits a
 * one-variant-bit different yet equally-correct `b.w` encoding
 * than the stock toolchain for these offsets. Internal
 * branches name local labels normally.
 *
 * The whole-image survey grades the span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so the leaf never executes
 * in the shipped image; the reconstruction documents the bytes
 * and pins the behavior the replaced head must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-4248e2-4263e0-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_cd_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_CD_ATTR __attribute__((used, naked, noinline))
extern open_cfw_bl006_cd_u32 open_cfw_bootloader_mspi_cq_enable_423f8e(
    open_cfw_bl006_cd_u32);
#else
#define OPEN_CFW_BL006_CD_ATTR __attribute__((used, noinline))
#endif

/* Leaf O: control-dispatcher remainder (436 B). */
OPEN_CFW_BL006_CD_ATTR
open_cfw_bl006_cd_u32 open_cfw_bootloader_mspi_control_rem_tail_42612c(
    open_cfw_bl006_cd_u32 *window,
    open_cfw_bl006_cd_u32 state_off,
    open_cfw_bl006_cd_u32 pool_off,
    open_cfw_bl006_cd_u32 index,
    const unsigned char *desc,
    const unsigned char *desc2,
    open_cfw_bl006_cd_u32 r2_in,
    open_cfw_bl006_cd_u32 r6_in,
    open_cfw_bl006_cd_u32 r7_in,
    open_cfw_bl006_cd_u32 sl_in,
    open_cfw_bl006_cd_u32 cq_result,
    unsigned entry,
    open_cfw_bl006_cd_u32 *r0_out,
    open_cfw_bl006_cd_u32 *exit_out)
{
#if defined(__arm__) || defined(__thumb__)
    /* Out-of-span exits and their reviewed spellings (stock
     * bytes in parentheses):
     * 0x42613E bne 0x4260F4, off -78 (d9 d1): .inst 0xD1D9
     * 0x42614A beq 0x4260F4, off -90 (d3 d0): .inst 0xD0D3
     * 0x42614E b.w 0x4252E8, off -3946 (ff f7 cb b8):
     *   .inst.w 0xF7FFB8CB
     * 0x42615A b.w 0x4252E8, off -3952 (ff f7 c5 b8):
     *   .inst.w 0xF7FFB8C5
     * 0x42616C b.w 0x4252E8, off -3976 (ff f7 bc b8):
     *   .inst.w 0xF7FFB8BC
     * 0x42619E b.w 0x4252E6, off -4028 (ff f7 a2 b8):
     *   .inst.w 0xF7FFB8A2
     * 0x4261A8 b.w 0x4252E8, off -4036 (ff f7 9e b8):
     *   .inst.w 0xF7FFB89E
     * 0x4261E6 b.w 0x4252E6, off -4100 (ff f7 7e b8):
     *   .inst.w 0xF7FFB87E
     * 0x4261FC b.w 0x4252E6, off -4122 (ff f7 73 b8):
     *   .inst.w 0xF7FFB873
     * 0x426212 b.w 0x4252E6, off -4144 (ff f7 68 b8):
     *   .inst.w 0xF7FFB868
     * 0x42621C b.w 0x4252E8, off -4152 (ff f7 64 b8):
     *   .inst.w 0xF7FFB864
     * 0x4262D6 b.w 0x4252E6, off -4340 (ff f7 06 b8):
     *   .inst.w 0xF7FFB806
     * 0x4262DC b.w 0x4252E8, off -4344 (ff f7 04 b8):
     *   .inst.w 0xF7FFB804
     * (`.inst.w` takes opcode halves in reading order:
     * first halfword high.) */
    __asm__ volatile(
        "ldr.w r0, [r5, #0x85c]\n"
        "adds r0, r0, #1\n"
        "str.w r0, [r5, #0x85c]\n"
        "mov r0, sl\n"
        "msr primask, r0\n"
        "cmp r6, #0\n"
        ".inst 0xD1D9\n"
        "movs r0, r7\n"
        "bl open_cfw_bootloader_mspi_cq_enable_423f8e\n"
        "movs r4, r0\n"
        "cmp r4, #0\n"
        ".inst 0xD0D3\n"
        "movs r0, r4\n"
        ".inst.w 0xF7FFB8CB\n"
        "movs r0, r2\n"
        "cmp r2, #0\n"
        "bne 0f\n"
        "movs r0, #6\n"
        ".inst.w 0xF7FFB8C5\n"
        "0: ldrb r1, [r0]\n"
        "cmp r1, #4\n"
        "bge 1f\n"
        "ldrb r1, [r0, #1]\n"
        "cmp r1, #2\n"
        "blt 2f\n"
        "1: movs r0, #6\n"
        ".inst.w 0xF7FFB8BC\n"
        "2: ldrb r2, [r0, #1]\n"
        "ands r2, r2, #1\n"
        "ldr.w r1, [pc, #0x68c]\n"
        "adds.w r3, r1, r6, lsl #12\n"
        "adds r3, #0x84\n"
        "ldr r4, [r3]\n"
        "bfi r4, r2, #7, #1\n"
        "str r4, [r3]\n"
        "ldrb r0, [r0]\n"
        "ands r0, r0, #3\n"
        "adds.w r1, r1, r6, lsl #12\n"
        "adds r1, #0x84\n"
        "ldr r2, [r1]\n"
        "bfi r2, r0, #5, #2\n"
        "str r2, [r1]\n"
        "movs r4, #0\n"
        ".inst.w 0xF7FFB8A2\n"
        "cmp r2, #0\n"
        "bne 3f\n"
        "movs r0, #6\n"
        ".inst.w 0xF7FFB89E\n"
        "3: ldrb r1, [r2, #9]\n"
        "ands r1, r1, #0x3f\n"
        "ldr.w r0, [pc, #0x650]\n"
        "adds.w r3, r0, r6, lsl #12\n"
        "adds r3, #0x84\n"
        "ldr r4, [r3]\n"
        "bfi r4, r1, #0x1a, #6\n"
        "str r4, [r3]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0x90\n"
        "movs r3, #5\n"
        "ldr r4, [r1]\n"
        "bfi r4, r3, #8, #4\n"
        "str r4, [r1]\n"
        "ldrb r1, [r2, #0xc]\n"
        "adds.w r0, r0, r6, lsl #12\n"
        "adds r0, #0x90\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0xd, #1\n"
        "str r2, [r0]\n"
        "movs r4, #0\n"
        ".inst.w 0xF7FFB87E\n"
        "ldr.w r0, [pc, #0x618]\n"
        "adds.w r0, r0, r6, lsl #12\n"
        "adds r0, #0x90\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x40\n"
        "str r1, [r0]\n"
        ".inst.w 0xF7FFB873\n"
        "ldr.w r0, [pc, #0x600]\n"
        "adds.w r0, r0, r6, lsl #12\n"
        "adds r0, r0, #0x90\n"
        "ldr r1, [r0]\n"
        "orrs r1, r1, #0x40\n"
        "str r1, [r0]\n"
        ".inst.w 0xF7FFB868\n"
        "cmp r2, #0\n"
        "bne 4f\n"
        "movs r0, #6\n"
        ".inst.w 0xF7FFB864\n"
        "4: ldrb r0, [r2, #4]\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "ldr.w r0, [pc, #0x5dc]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0xa4\n"
        "ldr r3, [r1]\n"
        "orrs r3, r3, #1\n"
        "str r3, [r1]\n"
        "ldrb r1, [r2]\n"
        "ands r1, r1, #3\n"
        "adds.w r3, r0, r6, lsl #12\n"
        "adds r3, #0xa4\n"
        "ldr r5, [r3]\n"
        "bfi r5, r1, #9, #2\n"
        "str r5, [r3]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0xa4\n"
        "ldr r3, [r1]\n"
        "bics r3, r3, #2\n"
        "str r3, [r1]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0xa4\n"
        "ldr r3, [r1]\n"
        "bics r3, r3, #4\n"
        "str r3, [r1]\n"
        "ldrb r1, [r2, #1]\n"
        "adds.w r3, r0, r6, lsl #12\n"
        "adds r3, #0xa4\n"
        "ldr r5, [r3]\n"
        "bfi r5, r1, #3, #1\n"
        "str r5, [r3]\n"
        "ldrb r1, [r2, #2]\n"
        "adds.w r3, r0, r6, lsl #12\n"
        "adds r3, #0xa4\n"
        "ldr r5, [r3]\n"
        "bfi r5, r1, #4, #1\n"
        "str r5, [r3]\n"
        "ldrb r1, [r2, #3]\n"
        "adds.w r2, r0, r6, lsl #12\n"
        "adds r2, #0xa4\n"
        "ldr r3, [r2]\n"
        "bfi r3, r1, #5, #1\n"
        "str r3, [r2]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0xa4\n"
        "ldr r2, [r1]\n"
        "bics r2, r2, #0x40\n"
        "str r2, [r1]\n"
        "adds.w r1, r0, r6, lsl #12\n"
        "adds r1, #0xa4\n"
        "ldr r2, [r1]\n"
        "bics r2, r2, #0x80\n"
        "str r2, [r1]\n"
        "adds.w r0, r0, r6, lsl #12\n"
        "adds r0, #0xa4\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x100\n"
        "str r1, [r0]\n"
        "b 6f\n"
        "5: ldr.w r0, [pc, #0x53c]\n"
        "adds.w r0, r0, r6, lsl #12\n"
        "adds r0, #0xa4\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #1\n"
        "lsls r1, r1, #1\n"
        "str r1, [r0]\n"
        "6: .inst.w 0xF7FFB806\n"
        "movs r0, #6\n"
        ".inst.w 0xF7FFB804\n");
#else
    /* Host twin: entry selects the stock entry (0-7 for
     * A0-A7); exit_out reports the rejoined head address class
     * (0 = E6 0x004252E6, 1 = E8 0x004252E8, 2 = head
     * 0x004260F4, non-returning). The window models the MSPI
     * aperture as byte offsets; descriptors arrive as host
     * byte arrays. r0_out carries the stock r0 at the exit
     * (a value or a register-address offset, per arm). */
    open_cfw_bl006_cd_u32 p84 = pool_off + (index << 12U) + 0x84U;
    open_cfw_bl006_cd_u32 p90 = pool_off + (index << 12U) + 0x90U;
    open_cfw_bl006_cd_u32 pa4 = pool_off + (index << 12U) + 0xA4U;
    (void)r7_in;
    (void)sl_in;
    switch (entry) {
    case 0U: {
        open_cfw_bl006_cd_u32 *ctr = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + state_off + 0x85CU);
        *ctr += 1U;
        if (r6_in != 0U) {
            *exit_out = 2U;
            *r0_out = 0U;
            return 0U;
        }
        if (cq_result == 0U) {
            *exit_out = 2U;
            *r0_out = 0U;
            return 0U;
        }
        *exit_out = 1U;
        *r0_out = cq_result;
        return 0U;
    }
    case 1U: {
        open_cfw_bl006_cd_u32 b0 = desc[0];
        open_cfw_bl006_cd_u32 b1 = desc[1];
        open_cfw_bl006_cd_u32 *w;
        if (b0 >= 4U || b1 >= 2U) {
            *exit_out = 1U;
            *r0_out = 6U;
            return 0U;
        }
        w = (open_cfw_bl006_cd_u32 *)((unsigned char *)window + p84);
        *w = (*w & (open_cfw_bl006_cd_u32)~0x80U) |
            ((b1 & 1U) << 7U);
        *w = (*w & (open_cfw_bl006_cd_u32)~0x60U) |
            ((b0 & 3U) << 5U);
        *exit_out = 0U;
        *r0_out = b0 & 3U;
        return 0U;
    }
    case 7U:
        *exit_out = 1U;
        *r0_out = 6U;
        return 0U;
    default:
        break;
    }
    if (entry == 2U && r2_in == 0U) {
        *exit_out = 1U;
        *r0_out = 6U;
        return 0U;
    }
    if (entry == 3U || (entry == 2U && r2_in != 0U)) {
        open_cfw_bl006_cd_u32 *w84 = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + p84);
        open_cfw_bl006_cd_u32 *w90 = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + p90);
        *w84 = (*w84 & (open_cfw_bl006_cd_u32)~0xFC000000U) |
            (((open_cfw_bl006_cd_u32)(desc2[9] & 0x3FU)) << 26U);
        *w90 = (*w90 & (open_cfw_bl006_cd_u32)~0xF00U) |
            (5U << 8U);
        *w90 = (*w90 & (open_cfw_bl006_cd_u32)~0x2000U) |
            (((open_cfw_bl006_cd_u32)(desc2[12] & 1U)) << 13U);
        *exit_out = 0U;
        *r0_out = p90;
        return 0U;
    }
    if (entry == 4U) {
        open_cfw_bl006_cd_u32 *w90 = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + p90);
        *w90 &= (open_cfw_bl006_cd_u32)~0x40U;
        *exit_out = 0U;
        *r0_out = p90;
        return 0U;
    }
    if (entry == 5U) {
        open_cfw_bl006_cd_u32 *w90 = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + p90);
        *w90 |= 0x40U;
        *exit_out = 0U;
        *r0_out = p90;
        return 0U;
    }
    /* Entry 6: third-descriptor configuration (see above). */
    {
        open_cfw_bl006_cd_u32 *wa4 = (open_cfw_bl006_cd_u32 *)
            ((unsigned char *)window + pa4);
        if (desc2[4] == 0U) {
            *wa4 &= (open_cfw_bl006_cd_u32)~1U;
            *exit_out = 0U;
            *r0_out = pa4;
            return 0U;
        }
        *wa4 |= 1U;
        *wa4 = (*wa4 & (open_cfw_bl006_cd_u32)~0x600U) |
            (((open_cfw_bl006_cd_u32)(desc2[0] & 3U)) << 9U);
        *wa4 &= (open_cfw_bl006_cd_u32)~2U;
        *wa4 &= (open_cfw_bl006_cd_u32)~4U;
        *wa4 = (*wa4 & (open_cfw_bl006_cd_u32)~0x8U) |
            (((open_cfw_bl006_cd_u32)(desc2[1] & 1U)) << 3U);
        *wa4 = (*wa4 & (open_cfw_bl006_cd_u32)~0x10U) |
            (((open_cfw_bl006_cd_u32)(desc2[2] & 1U)) << 4U);
        *wa4 = (*wa4 & (open_cfw_bl006_cd_u32)~0x20U) |
            (((open_cfw_bl006_cd_u32)(desc2[3] & 1U)) << 5U);
        *wa4 &= (open_cfw_bl006_cd_u32)~0x40U;
        *wa4 &= (open_cfw_bl006_cd_u32)~0x80U;
        *wa4 &= (open_cfw_bl006_cd_u32)~0x100U;
        *exit_out = 0U;
        *r0_out = pa4;
        return 0U;
    }
#endif
}


#if defined(__arm__) || defined(__thumb__)
/* Assembler probes: each emits one narrow out-of-span exit at
 * the identical byte offset, proving the reviewed `.inst`
 * spelling. (The eleven wide exits cannot carry probes: the
 * reference assembler emits a variant `b.w` encoding; they are
 * pinned by decoder verification instead.) Probe sections are
 * discarded from the firmware image. */
OPEN_CFW_BL006_CD_ATTR
void open_cfw_bl006_cd_probe_bne_78_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 74\n"
        "bne 0b\n");
}

OPEN_CFW_BL006_CD_ATTR
void open_cfw_bl006_cd_probe_beq_90_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 86\n"
        "beq 0b\n");
}
#endif
