/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of one dead G2 bootloader interior:
 *
 *  P. MSPI public device-configuration remainder at
 *     0x00424E84..0x00425066 (482 B), the surviving body of the
 *     replaced stock public device-configuration service (live
 *     replacement: the source-owned public device-configuration
 *     body that returns before this span). Thirteen entries, all
 *     fed only from the replaced head:
 *       E_main at 0x00424E84: register-bit setup, then the full
 *         configuration build below; returns 0 (or 5 on the
 *         divider reject path).
 *       E_div0-8 at 0x00424EA2..0x00424ED6: divider-select arms;
 *         each ORs one constant (0x20000, 0x30000, 0x40000,
 *         0x60000, 0x80000, 0xC0000, 0x100000, 0x180000,
 *         0x200000) into r2 and exits to the head (0x00424E5C).
 *       E_fail at 0x00424ED8: returns 5 through the shared pop.
 *       E_jump at 0x00424EDC: re-enters the head (0x00424E6E)
 *         with no effect.
 *       E_beq at 0x00424EE2: conditional bit-0 publish, then
 *         rejoins the main build.
 *     The main build assembles the 0x90/0x94/0x98 control words
 *     from the configuration and state bytes, programs the
 *     divider fields (with the reject path returning 5), invokes
 *     the in-place device-configuration and XIP-delay services
 *     (their results are discarded by stock), and returns 0
 *     through `pop {r1, r4-r7, pc}`.
 *     The single pool load reuses the retained pool word at
 *     0x004251B8 through its stock PC-relative offset
 *     (bitmap-client precedent; no relocation involved).
 *
 * Calls: the device-configuration and XIP-delay calls target the
 * source-owned in-place services
 * `open_cfw_bootloader_mspi_device_configure_424120` and
 * `open_cfw_bootloader_mspi_xip_off_delay_424a18`, named as
 * reviewed R_ARM_THM_CALL relocations. All ten out-of-span
 * narrow exits into the replaced head are spelled with reviewed
 * 16-bit encodings (`.inst`, binary32-tail precedent); nine
 * in-source probes prove the reference assembler emits the
 * identical bytes at the identical offsets (the two -114 exits
 * share one encoding). Internal branches name unique Q-labels:
 * numeric local labels miscompile in this ten-target block
 * (undefined `.Ltmp` temporaries alongside the two `bl`
 * relocations), while the named form assembles byte-exact.
 *
 * The whole-image survey grades the span
 * corroborated_unreachable_control_flow and a whole-image `bl`
 * sweep finds no caller of any entry, so the leaf never executes
 * in the shipped image; the reconstruction documents the bytes
 * and pins the behavior the replaced head must cover. See
 * docs/research/g2-bootloader-bl006-tail-leaves-4248e2-4263e0-source-closure.md.
 */

typedef __UINT32_TYPE__ open_cfw_bl006_dc2_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_DC2_ATTR __attribute__((used, naked, noinline))
extern open_cfw_bl006_dc2_u32 open_cfw_bootloader_mspi_device_configure_424120(
    open_cfw_bl006_dc2_u32);
extern open_cfw_bl006_dc2_u32 open_cfw_bootloader_mspi_xip_off_delay_424a18(
    open_cfw_bl006_dc2_u32);
#else
#define OPEN_CFW_BL006_DC2_ATTR __attribute__((used, noinline))
#endif

/* Leaf P: public device-configuration remainder (482 B). */
OPEN_CFW_BL006_DC2_ATTR
open_cfw_bl006_dc2_u32 open_cfw_bootloader_mspi_devconfig_rem_tail_424e84(
    open_cfw_bl006_dc2_u32 *window,
    open_cfw_bl006_dc2_u32 base_off,
    open_cfw_bl006_dc2_u32 index,
    const unsigned char *cfg,
    unsigned char *state,
    open_cfw_bl006_dc2_u32 pool_limit,
    open_cfw_bl006_dc2_u32 r2_in,
    unsigned entry,
    open_cfw_bl006_dc2_u32 *r0_out,
    open_cfw_bl006_dc2_u32 *exit_out)
{
#if defined(__arm__) || defined(__thumb__)
    /* Out-of-span exits and their reviewed spellings (stock
     * bytes in parentheses); all are narrow `b`:
     * -78 (d9 e7): .inst 0xE7D9; -84 (d6 e7): .inst 0xE7D6;
     * -90 (d3 e7): .inst 0xE7D3; -96 (d0 e7): .inst 0xE7D0;
     * -102 (cd e7): .inst 0xE7CD; -108 (ca e7): .inst 0xE7CA;
     * -114 (c7 e7): .inst 0xE7C7; -120 (c4 e7): .inst 0xE7C4;
     * -126 (c1 e7): .inst 0xE7C1. */
    __asm__ volatile(
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x88\n"
        "ldr r2, [r0]\n"
        "orrs r2, r2, #1\n"
        "str r2, [r0]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x8c\n"
        "ldr r2, [r0]\n"
        "orrs r2, r2, #0x80000000\n"
        "str r2, [r0]\n"
        "b Q2\n"
        "orrs r2, r2, #0x20000\n"
        ".inst 0xE7D9\n"
        "orrs r2, r2, #0x30000\n"
        ".inst 0xE7D6\n"
        "orrs r2, r2, #0x40000\n"
        ".inst 0xE7D3\n"
        "orrs r2, r2, #0x60000\n"
        ".inst 0xE7D0\n"
        "orrs r2, r2, #0x80000\n"
        ".inst 0xE7CD\n"
        "orrs r2, r2, #0xc0000\n"
        ".inst 0xE7CA\n"
        "orrs r2, r2, #0x100000\n"
        ".inst 0xE7C7\n"
        "orrs r2, r2, #0x180000\n"
        ".inst 0xE7C4\n"
        "orrs r2, r2, #0x200000\n"
        ".inst 0xE7C1\n"
        "movs r0, #5\n"
        "b Q7\n"
        ".inst 0xE7C7\n"
        "movs r0, #5\n"
        "b Q7\n"
        "ldrb r0, [r4, #0x10]\n"
        "cmp r0, #0\n"
        "beq Q0\n"
        "movs r0, #1\n"
        "b Q1\n"
        "Q0: movs r0, #0\n"
        "Q1: adds.w r2, r1, r6, lsl #12\n"
        "adds r2, #0x88\n"
        "ldr r3, [r2]\n"
        "bfi r3, r0, #0, #1\n"
        "str r3, [r2]\n"
        "Q2: ldrb r0, [r4, #0x12]\n"
        "ands r0, r0, #3\n"
        "adds.w r2, r1, r6, lsl #12\n"
        "adds r2, #0x8c\n"
        "ldr r3, [r2]\n"
        "bfi r3, r0, #0x11, #2\n"
        "str r3, [r2]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x30\n"
        "ldr r2, [r0]\n"
        "lsrs r2, r2, #1\n"
        "lsls r2, r2, #1\n"
        "str r2, [r0]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "ldr.w r0, [r0, #0x90]\n"
        "ldr r2, [pc, #0x290]\n"
        "ands r2, r0\n"
        "orrs r2, r2, #0xc\n"
        "ldrb r0, [r5, #0xd]\n"
        "orrs.w r2, r2, r0, lsl #4\n"
        "ldrb r0, [r4, #0xf]\n"
        "cmp r0, #0\n"
        "beq Q3\n"
        "orrs r2, r2, #0x20\n"
        "movs r0, r2\n"
        "ldrb r2, [r4]\n"
        "lsls r2, r2, #0xe\n"
        "ands r2, r2, #0xfc000\n"
        "orrs r2, r0\n"
        "Q3: ldrb r0, [r4, #0xd]\n"
        "cmp r0, #0\n"
        "beq Q4\n"
        "orrs r2, r2, #0x40\n"
        "Q4: ldrb r0, [r4, #0xe]\n"
        "cmp r0, #0\n"
        "beq Q5\n"
        "orrs r2, r2, #0x80\n"
        "Q5: ldrb r0, [r4, #0xc]\n"
        "orrs.w r2, r2, r0, lsl #13\n"
        "ldrb r0, [r4, #9]\n"
        "lsls r0, r0, #0x14\n"
        "ands r0, r0, #0x3f00000\n"
        "orrs r2, r0\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "str.w r2, [r0, #0x90]\n"
        "movs r2, #0\n"
        "ldrh r0, [r4, #6]\n"
        "orrs r2, r0\n"
        "ldrh r0, [r4, #4]\n"
        "orrs.w r2, r2, r0, lsl #16\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "str.w r2, [r0, #0x94]\n"
        "movs r0, #0\n"
        "ldrh r2, [r4, #0x14]\n"
        "lsls r2, r2, #0x14\n"
        "lsrs r2, r2, #0x14\n"
        "orrs r0, r2\n"
        "ldrb r2, [r4, #0x16]\n"
        "lsls r2, r2, #0xc\n"
        "ands r2, r2, #0xf000\n"
        "orrs r0, r2\n"
        "adds.w r2, r1, r6, lsl #12\n"
        "str.w r0, [r2, #0x98]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x30\n"
        "movs r2, #7\n"
        "ldr r3, [r0]\n"
        "bfi r3, r2, #4, #4\n"
        "str r3, [r0]\n"
        "movs r0, #0\n"
        "strb r0, [r5, #0xd]\n"
        "ldr r0, [r5, #0x18]\n"
        "cmp r0, #0\n"
        "beq Q6\n"
        "movs r0, #0x20\n"
        "adds.w r2, r1, r6, lsl #12\n"
        "str.w r0, [r2, #0x114]\n"
        "ldrb r0, [r4, #0xb]\n"
        "subs r0, r0, #1\n"
        "cmp r0, #0x10\n"
        "bls Q8\n"
        "subs r0, #0x11\n"
        "cmp r0, #5\n"
        "bhi Q9\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds.w r0, r0, #0x118\n"
        "movs r2, #0xc\n"
        "ldr r3, [r0]\n"
        "bfi r3, r2, #0, #5\n"
        "str r3, [r0]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x20\n"
        "movs r2, #0x1e\n"
        "ldr r3, [r0]\n"
        "bfi r3, r2, #8, #6\n"
        "str r3, [r0]\n"
        "adds.w r1, r1, r6, lsl #12\n"
        "adds.w r0, r1, #0x118\n"
        "movs r1, #8\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #8, #5\n"
        "str r2, [r0]\n"
        "Q6: ldrb r0, [r4, #8]\n"
        "strb r0, [r5, #0xa]\n"
        "movs r0, r5\n"
"bl open_cfw_bootloader_mspi_device_configure_424120\n"
        "movs r0, #0\n"
        "strb r0, [r5, #0xd]\n"
        "ldrb r0, [r4, #0xb]\n"
        "strb r0, [r5, #0xc]\n"
        "movw r0, #0x2710\n"
        "str r0, [r5, #0x10]\n"
        "movs r0, r5\n"
"bl open_cfw_bootloader_mspi_xip_off_delay_424a18\n"
        "movs r0, #0\n"
        "Q7: pop {r1, r4, r5, r6, r7, pc}\n"
        "Q8: adds.w r0, r1, r6, lsl #12\n"
        "adds.w r0, r0, #0x118\n"
        "movs r2, #8\n"
        "ldr r3, [r0]\n"
        "bfi r3, r2, #0, #5\n"
        "str r3, [r0]\n"
        "adds.w r0, r1, r6, lsl #12\n"
        "adds r0, #0x20\n"
        "movs r3, #0x1e\n"
        "ldr r7, [r0]\n"
        "bfi r7, r3, #8, #6\n"
        "str r7, [r0]\n"
        "adds.w r1, r1, r6, lsl #12\n"
        "adds.w r0, r1, #0x118\n"
        "ldr r1, [r0]\n"
        "bfi r1, r2, #8, #5\n"
        "str r1, [r0]\n"
        "b Q6\n"
        "Q9: movs r0, #5\n"
        "b Q7\n" );
#else
    /* Host twin: entry selects the stock entry (0 = main,
     * 1-9 = divider arms, 10 = fail stub, 11 = head jump,
     * 12 = conditional bit-0 path). exit_out reports the class
     * (0 = shared pop return, 1 = fail return 5 through the
     * pop, 2 = head re-entry, non-returning). The window models
     * the MSPI aperture as byte offsets; cfg/state arrive as
     * host byte arrays; the pool limit word arrives explicitly.
     * The two callee results are discarded by stock, so the
     * twin does not take them. */
    static const open_cfw_bl006_dc2_u32 divs[9] = {
        0x20000U, 0x30000U, 0x40000U, 0x60000U, 0x80000U,
        0xC0000U, 0x100000U, 0x180000U, 0x200000U};
    open_cfw_bl006_dc2_u32 b = base_off + (index << 12U);
    if (entry >= 1U && entry <= 9U) {
        *r0_out = r2_in | divs[entry - 1U];
        *exit_out = 2U;
        return 0U;
    }
    if (entry == 10U) {
        *r0_out = 5U;
        *exit_out = 1U;
        return 0U;
    }
    if (entry == 11U) {
        *r0_out = 0U;
        *exit_out = 2U;
        return 0U;
    }
    if (entry == 0U) {
        open_cfw_bl006_dc2_u32 *w =
            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x88U);
        *w |= 1U;
        w = (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x8CU);
        *w |= 0x80000000U;
    } else {
        open_cfw_bl006_dc2_u32 *w =
            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x88U);
        *w = (*w & (open_cfw_bl006_dc2_u32)~1U) |
            (cfg[0x10] ? 1U : 0U);
    }
    {
        open_cfw_bl006_dc2_u32 *w =
            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x8CU);
        open_cfw_bl006_dc2_u32 *w30 =
            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x30U);
        open_cfw_bl006_dc2_u32 *w90 =
            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x90U);
        open_cfw_bl006_dc2_u32 r2;
        *w = (*w & (open_cfw_bl006_dc2_u32)~(3U << 17U)) |
            (((open_cfw_bl006_dc2_u32)(cfg[0x12] & 3U)) << 17U);
        *w30 &= (open_cfw_bl006_dc2_u32)~1U;
        r2 = (*w90 & pool_limit) | 0xCU;
        r2 |= ((open_cfw_bl006_dc2_u32)state[0xD]) << 4U;
        if (cfg[0xF]) {
            r2 |= 0x20U;
        }
        r2 = (((open_cfw_bl006_dc2_u32)cfg[0] << 14U) & 0xFC000U) | r2;
        if (cfg[0xD]) {
            r2 |= 0x40U;
        }
        if (cfg[0xE]) {
            r2 |= 0x80U;
        }
        r2 |= ((open_cfw_bl006_dc2_u32)cfg[0xC]) << 13U;
        r2 |= (((open_cfw_bl006_dc2_u32)cfg[9] << 20U) & 0x3F00000U);
        *w90 = r2;
        {
            open_cfw_bl006_dc2_u32 lo =
                (open_cfw_bl006_dc2_u32)cfg[6] |
                (((open_cfw_bl006_dc2_u32)cfg[7]) << 8U);
            open_cfw_bl006_dc2_u32 hi =
                (open_cfw_bl006_dc2_u32)cfg[4] |
                (((open_cfw_bl006_dc2_u32)cfg[5]) << 8U);
            open_cfw_bl006_dc2_u32 *w94 =
                (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x94U);
            *w94 = lo | (hi << 16U);
        }
        {
            open_cfw_bl006_dc2_u32 v14 =
                (open_cfw_bl006_dc2_u32)cfg[0x14] |
                (((open_cfw_bl006_dc2_u32)cfg[0x15]) << 8U);
            open_cfw_bl006_dc2_u32 r0 =
                (v14 & 0xFFFFFU) |
                ((((open_cfw_bl006_dc2_u32)cfg[0x16]) << 12U) & 0xF000U);
            open_cfw_bl006_dc2_u32 *w98 =
                (open_cfw_bl006_dc2_u32 *)((unsigned char *)window + b + 0x98U);
            *w98 = r0;
        }
        *w30 = (*w30 & (open_cfw_bl006_dc2_u32)~(0xFU << 4U)) |
            (7U << 4U);
        state[0xD] = 0;
        {
            open_cfw_bl006_dc2_u32 s18 =
                (open_cfw_bl006_dc2_u32)state[0x18] |
                (((open_cfw_bl006_dc2_u32)state[0x19]) << 8U) |
                (((open_cfw_bl006_dc2_u32)state[0x1A]) << 16U) |
                (((open_cfw_bl006_dc2_u32)state[0x1B]) << 24U);
            if (s18 != 0U) {
                open_cfw_bl006_dc2_u32 *w114 =
                    (open_cfw_bl006_dc2_u32 *)((unsigned char *)window +
                        b + 0x114U);
                open_cfw_bl006_dc2_u32 b1 =
                    (open_cfw_bl006_dc2_u32)(((unsigned)cfg[0xB] - 1U) & 0xFFU);
                *w114 = 0x20U;
                if (b1 <= 0x10U) {
                    open_cfw_bl006_dc2_u32 *w118 =
                        (open_cfw_bl006_dc2_u32 *)((unsigned char *)window +
                            b + 0x118U);
                    open_cfw_bl006_dc2_u32 *w20 =
                        (open_cfw_bl006_dc2_u32 *)((unsigned char *)window +
                            b + 0x20U);
                    *w118 = (*w118 & (open_cfw_bl006_dc2_u32)~0x1FU) | 8U;
                    *w20 = (*w20 &
                        (open_cfw_bl006_dc2_u32)~(0x3FU << 8U)) |
                        (0x1EU << 8U);
                    *w118 = (*w118 &
                        (open_cfw_bl006_dc2_u32)~(0x1FU << 8U)) |
                        (8U << 8U);
                } else {
                    b1 = (b1 - 0x11U) & 0xFFU;
                    if (b1 > 5U) {
                        *r0_out = 5U;
                        *exit_out = 1U;
                        return 0U;
                    }
                    {
                        open_cfw_bl006_dc2_u32 *w118 =
                            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window +
                                b + 0x118U);
                        open_cfw_bl006_dc2_u32 *w20 =
                            (open_cfw_bl006_dc2_u32 *)((unsigned char *)window +
                                b + 0x20U);
                        *w118 = (*w118 &
                            (open_cfw_bl006_dc2_u32)~0x1FU) | 0xCU;
                        *w20 = (*w20 &
                            (open_cfw_bl006_dc2_u32)~(0x3FU << 8U)) |
                            (0x1EU << 8U);
                        *w118 = (*w118 &
                            (open_cfw_bl006_dc2_u32)~(0x1FU << 8U)) |
                            (8U << 8U);
                    }
                }
            }
        }
        state[0xA] = cfg[8];
        state[0xD] = 0;
        state[0xC] = cfg[0xB];
        state[0x10] = 0x10U;
        state[0x11] = 0x27U;
        state[0x12] = 0U;
        state[0x13] = 0U;
        *r0_out = 0U;
        *exit_out = 0U;
        return 0U;
    }
#endif
}

#if defined(__arm__) || defined(__thumb__)
/* Assembler probes: each emits one out-of-span narrow exit at the
 * identical byte offset, proving the reviewed `.inst` spelling.
 * Probe sections are discarded from the firmware image. */

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_78_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 74\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_84_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 80\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_90_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 86\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_96_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 92\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_102_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 98\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_108_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 104\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_114_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 110\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_120_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 116\n"
        "b 0b\n");
}

OPEN_CFW_BL006_DC2_ATTR
void open_cfw_bl006_dc2_probe_b_126_back(void)
{
    __asm__ volatile(
        "0:\n"
        ".space 122\n"
        "b 0b\n");
}
#endif
