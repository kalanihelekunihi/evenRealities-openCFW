/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the last retained BL-006 span:
 *
 *   0x00427E54..0x00428378 (1,316 B): three SPOT trim-search
 *   services plus the float classifier suffix tail that selects
 *   a trim index from a float reading. Each subspan is the dead
 *   surviving end of an entry-redirect-replaced head; the
 *   whole-image retained survey grades the span
 *   corroborated_unreachable_control_flow and a whole-image `bl`
 *   sweep finds no caller of any of the four entries, so no leaf
 *   executes in the shipped image. The reconstructions document
 *   the bytes and pin the behavior the replaced heads cover.
 *
 *   T0  0x00427E54..0x00427E84 (48 B): suffix tail of the stock
 *       float classifier. Entry FPSCR (set by the replaced head)
 *       N flag set -> return 2. Else compare s0 against 50.0f
 *       (pool 0x00428060 = 0x42480000) and 1000.0f (pool
 *       0x00428064 = 0x447A0000): below 50.0 -> 4, in
 *       [50.0, 1000.0) -> 3, at/above 1000.0 -> 4. NaN is
 *       unordered (VCMP sets N=Z=C=V=1, so neither blt nor bpl
 *       is taken) and returns 3. No calls, no relocations.
 *   F1  0x00427E84..0x00428068 (484 B): trim-search variant A.
 *       On entry r0 = trim id, r1 = table index, r2 = client
 *       word. Either the trim-match path (gate word bit0 set
 *       and trim id matches: ton-adjust, control merge,
 *       finalize, status byte 0x1A) or the measure path (60x
 *       delay-poll loop, timer service, SRAM publishes,
 *       ton-adjust, saturating trim clamp into 0x4002004C,
 *       delay, pulse merge, conditional IRQ pause, power bit
 *       sets, delay, conditional IRQ resume, field publishes
 *       into 0x40020080 and 0x40020044). Nine reviewed
 *       R_ARM_THM_CALL relocations, all to source-owned
 *       symbols. The 14-byte tail after the return is
 *       alignment plus the float pool T0 reads (a 2-byte zero
 *       pad, the head-owned word 0xC3888000 retained verbatim,
 *       50.0f, 1000.0f), reproduced exactly.
 *   F2  0x00428068..0x00428240 (472 B): trim-search variant B
 *       (no trim-match/finalize path; two trim clamps, one
 *       into 0x4002004C and one into 0x40020044; extra power
 *       bit sets). Eight reviewed call relocations. Ends
 *       exactly at its return.
 *   F3  0x00428240..0x00428378 (312 B): trim-search variant C
 *       (no IRQ pause/resume; merges the word at table+0x50
 *       into 0x4002004C, one trim clamp, stores the trim id,
 *       then transition_start(50) and status byte 0x02).
 *       Four reviewed call relocations. Ends exactly at its
 *       return.
 *
 * The scratch-byte selects (four trim bytes split from the
 * table word at +0x64) are dead in all three variants: both
 * loaded bytes are overwritten before any use. The twins omit
 * them. F2/F3 reload r0 from sl before ton-adjust, so ton-adjust
 * always receives (sl, r4) on every path; the twins record that
 * directly. Returns are stack-restored head garbage; the twins
 * return 0.
 *
 * The 16 external pool slots these bodies read stay retained
 * under the SPOT work items (0x004283E2.. region); the leaves
 * reuse them through stock PC-relative offsets
 * (bitmap-client precedent), so the bodies assemble with plain
 * mnemonics and exact immediates.
 *
 * See docs/research/g2-bootloader-bl006-span-427e54-spot-trim-source-closure.md
 * (this turn) and g2-bootloader-bl006-span-427e54-spot-trim-survey.md
 * (the structural survey this closes).
 */

typedef __UINT32_TYPE__ open_cfw_bl006_spot_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BL006_SPOT_ATTR __attribute__((used, naked, noinline))
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_trim_finalize_41ccd6(void);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_retained_delay_41d1c0(
    open_cfw_bl006_spot_u32);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_irq_resume_41e1e8(void);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_irq_pause_41e22e(void);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_timer_irq_service_42a04a(void);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc(
    open_cfw_bl006_spot_u32, open_cfw_bl006_spot_u32);
extern open_cfw_bl006_spot_u32 open_cfw_bootloader_spotmgr_transition_start_41cc48(
    open_cfw_bl006_spot_u32);
#else
#define OPEN_CFW_BL006_SPOT_ATTR __attribute__((used, noinline))
#endif

/* Host memory-image slot order (absolute addresses documented
 * so the twin's slot traffic matches the stock pool targets):
 * 0: 0x400083E0 gate (bit0) | 1: 0x20000154 trim id |
 * 2: 0x40008064 delay poll (bit30) | 3: 0x40020044 control |
 * 4: 0x4002004C pulse/clamp | 5: 0xE000ED14 pause poll (bit17) |
 * 6: 0x4002037C power sets | 7: 0x40020080 field publish |
 * 8: 0x200270C0 | 9: 0x200270C4 | 10: 0x200270B8 |
 * 11: 0x200270BC | 12: 0x200270B0 | 13: 0x200270B4 |
 * 14: 0x2000055A status byte cell (low 8 bits used). */
enum {
    OPEN_CFW_BL006_SPOT_GATE = 0,
    OPEN_CFW_BL006_SPOT_TRIMID,
    OPEN_CFW_BL006_SPOT_POLL,
    OPEN_CFW_BL006_SPOT_CTRL44,
    OPEN_CFW_BL006_SPOT_PULSE4C,
    OPEN_CFW_BL006_SPOT_SYSTICK,
    OPEN_CFW_BL006_SPOT_PWR37C,
    OPEN_CFW_BL006_SPOT_PWR280,
    OPEN_CFW_BL006_SPOT_SRAM_C0,
    OPEN_CFW_BL006_SPOT_SRAM_C4,
    OPEN_CFW_BL006_SPOT_SRAM_B8,
    OPEN_CFW_BL006_SPOT_SRAM_BC,
    OPEN_CFW_BL006_SPOT_SRAM_B0,
    OPEN_CFW_BL006_SPOT_SRAM_B4,
    OPEN_CFW_BL006_SPOT_SRAM_55A,
    OPEN_CFW_BL006_SPOT_NSLOT
};

typedef struct {
    open_cfw_bl006_spot_u32 w[OPEN_CFW_BL006_SPOT_NSLOT];
} open_cfw_bl006_spot_mem;

typedef struct {
    open_cfw_bl006_spot_u32 delay_calls, delay_last;
    open_cfw_bl006_spot_u32 pause_calls, resume_calls;
    open_cfw_bl006_spot_u32 timer_calls, finalize_calls, transstart_calls;
    open_cfw_bl006_spot_u32 transstart_arg;
    open_cfw_bl006_spot_u32 ton_calls, ton_a0, ton_a1;
} open_cfw_bl006_spot_calls;

/* Leaf T0: float classifier suffix tail (48 B). */
OPEN_CFW_BL006_SPOT_ATTR
open_cfw_bl006_spot_u32 open_cfw_bootloader_spot_trim_classify_tail_427e54(
    open_cfw_bl006_spot_u32 r4_in, float s0_in, open_cfw_bl006_spot_u32 n_in)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
"lsrs r0, r4, #9\n"
"vmrs apsr_nzcv, fpscr\n"
"bpl L_t0_427e60\n"
"movs r0, #2\n"
"b L_t0_427e82\n"
"L_t0_427e60:\n"
"vldr s1, [pc, #0x1fc]\n"
"vcmp.f32 s0, s1\n"
"vmrs apsr_nzcv, fpscr\n"
"blt L_t0_427e80\n"
"vldr s1, [pc, #0x1f4]\n"
"vcmp.f32 s0, s1\n"
"vmrs apsr_nzcv, fpscr\n"
"bpl L_t0_427e80\n"
"movs r0, #3\n"
"b L_t0_427e82\n"
"L_t0_427e80:\n"
"movs r0, #4\n"
"L_t0_427e82:\n"
"bx lr\n");
#else
    /* Host twin: the entry N flag arrives explicitly (head-owned
     * compare); s0 arrives as a float. Unordered (NaN) falls
     * through both compares to 3, matching the VCMP N=Z=C=V=1
     * encoding under which neither blt nor bpl is taken. */
    (void)r4_in;
    if (n_in & 1U) {
        return 2U;
    }
    {
        int is_unordered = (s0_in != s0_in);
        if (is_unordered) {
            return 3U;
        }
    }
    if (s0_in < 50.0f) {
        return 4U;
    }
    if (s0_in < 1000.0f) {
        return 3U;
    }
    return 4U;
#endif
}

/* Leaf F1: trim-search variant A (484 B, incl. the 14-byte
 * alignment/float-pool tail the return precedes). */
OPEN_CFW_BL006_SPOT_ATTR
open_cfw_bl006_spot_u32 open_cfw_bootloader_spot_trim_search_a_427e84(
    open_cfw_bl006_spot_u32 r0_in, open_cfw_bl006_spot_u32 r1_in,
    open_cfw_bl006_spot_u32 r2_in, const open_cfw_bl006_spot_u32 *tab_in,
    open_cfw_bl006_spot_mem *mem_in, open_cfw_bl006_spot_calls *calls_in)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
"push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n"
"movs r4, r0\n"
"movs r5, r2\n"
"movs r6, #0\n"
"ldr.w r0, [pc, #0xbe8]\n"
"add.w r2, r0, r4, lsl #2\n"
"adds r7, r2, #4\n"
"add.w r2, r0, r1, lsl #2\n"
"adds r2, r2, #4\n"
"adds.w r3, r0, #0x64\n"
"ldrb r0, [r3]\n"
"ands r0, r0, #0x7f\n"
"strb.w r0, [sp]\n"
"mov r0, sp\n"
"ldr.w ip, [r3]\n"
"lsrs.w ip, ip, #7\n"
"ands ip, ip, #0x7f\n"
"strb.w ip, [r0, #1]\n"
"ldr.w ip, [r3]\n"
"lsrs.w ip, ip, #0xe\n"
"ands ip, ip, #0x7f\n"
"strb.w ip, [r0, #2]\n"
"ldr r3, [r3]\n"
"lsrs r3, r3, #0x15\n"
"ands r3, r3, #0x7f\n"
"strb r3, [r0, #3]\n"
"ldrb.w r8, [r2]\n"
"ands r8, r8, #0x7f\n"
"ldr r2, [r2]\n"
"ubfx r2, r2, #0x15, #7\n"
"ldr r2, [r7]\n"
"ubfx sb, r2, #0x15, #7\n"
"ldrb.w sl, [r7]\n"
"ands sl, sl, #0x7f\n"
"ands r1, r1, #3\n"
"ldrb r1, [r0, r1]\n"
"ands r1, r4, #3\n"
"ldrb r0, [r0, r1]\n"
"ldr.w r0, [pc, #0xb78]\n"
"ldr r1, [r0]\n"
"lsls r1, r1, #0x1f\n"
"bpl L_f1_427f66\n"
"ldr.w r1, [pc, #0xb74]\n"
"ldr r1, [r1]\n"
"cmp r4, r1\n"
"bne L_f1_427f3c\n"
"movs r1, r4\n"
"movs r0, r5\n"
"bl open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc\n"
"ldr.w r0, [pc, #0xd64]\n"
"ldr r1, [r0]\n"
"lsrs r1, r1, #7\n"
"lsls r1, r1, #7\n"
"orrs.w sb, sb, r1\n"
"str.w sb, [r0]\n"
"bl open_cfw_bootloader_spotmgr_trim_finalize_41ccd6\n"
"movs r0, #0x1a\n"
"ldr.w r1, [pc, #0xd50]\n"
"strb r0, [r1]\n"
"b L_f1_428056\n"
"L_f1_427f3c:\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #0x1f\n"
"bpl L_f1_427f66\n"
"movs.w fp, #0\n"
"b L_f1_427f52\n"
"L_f1_427f48:\n"
"movs r0, #1\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"adds.w fp, fp, #1\n"
"L_f1_427f52:\n"
"cmp.w fp, #0x3c\n"
"bhs L_f1_427f62\n"
"ldr.w r0, [pc, #0xb28]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #1\n"
"bpl L_f1_427f48\n"
"L_f1_427f62:\n"
"bl open_cfw_bootloader_spotmgr_timer_irq_service_42a04a\n"
"L_f1_427f66:\n"
"ldr.w r0, [pc, #0xb20]\n"
"str r5, [r0]\n"
"ldr.w r0, [pc, #0xb1c]\n"
"str r4, [r0]\n"
"ldr r0, [r7]\n"
"ubfx r0, r0, #7, #0xa\n"
"ldr.w r1, [pc, #0xd14]\n"
"str r0, [r1]\n"
"ldr r0, [r7]\n"
"ubfx r0, r0, #0x11, #4\n"
"ldr.w r1, [pc, #0xd0c]\n"
"str r0, [r1]\n"
"ldr.w r0, [pc, #0xd0c]\n"
"str.w sb, [r0]\n"
"ldr.w r0, [pc, #0xafc]\n"
"str.w sl, [r0]\n"
"movs r1, r4\n"
"movs r0, r5\n"
"bl open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc\n"
"subs.w r0, sl, r8\n"
"cmp r0, #1\n"
"blt L_f1_427fae\n"
"lsls r0, r0, #1\n"
"b L_f1_427fb0\n"
"L_f1_427fae:\n"
"movs r0, #0\n"
"L_f1_427fb0:\n"
"adds.w r1, r0, r8\n"
"cmp r1, #0x80\n"
"blo L_f1_427fc6\n"
"ldr.w r0, [pc, #0xbec]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x7f\n"
"str r1, [r0]\n"
"b L_f1_427fd6\n"
"L_f1_427fc6:\n"
"ldr.w r1, [pc, #0xbe0]\n"
"adds.w r8, r0, r8\n"
"ldr r0, [r1]\n"
"bfi r0, r8, #0, #7\n"
"str r0, [r1]\n"
"L_f1_427fd6:\n"
"movs r0, #0x32\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"ldr.w r0, [pc, #0xbc8]\n"
"ldr r1, [r0]\n"
"lsrs r1, r1, #7\n"
"lsls r1, r1, #7\n"
"orrs.w sl, sl, r1\n"
"str.w sl, [r0]\n"
"ldr.w r0, [pc, #0xbbc]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #0xe\n"
"bpl L_f1_427ffe\n"
"bl open_cfw_bootloader_spotmgr_irq_pause_41e22e\n"
"movs r6, #1\n"
"L_f1_427ffe:\n"
"ldr.w r0, [pc, #0xc9c]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x10000\n"
"str r1, [r0]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x2000000\n"
"str r1, [r0]\n"
"movs r0, #0x14\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"uxtb r6, r6\n"
"cmp r6, #0\n"
"beq L_f1_428022\n"
"bl open_cfw_bootloader_spotmgr_irq_resume_41e1e8\n"
"L_f1_428022:\n"
"ldr r0, [r7]\n"
"ubfx r0, r0, #0x11, #4\n"
"ldr.w r1, [pc, #0xc74]\n"
"ldr r2, [r1]\n"
"bfi r2, r0, #0xa, #4\n"
"str r2, [r1]\n"
"ldr r0, [r7]\n"
"ubfx r0, r0, #7, #0xa\n"
"ldr r2, [r1]\n"
"lsrs r2, r2, #0xa\n"
"lsls r2, r2, #0xa\n"
"orrs r0, r2\n"
"str r0, [r1]\n"
"ldr.w r0, [pc, #0xc3c]\n"
"ldr r1, [r0]\n"
"lsrs r1, r1, #7\n"
"lsls r1, r1, #7\n"
"orrs.w sb, sb, r1\n"
"str.w sb, [r0]\n"
"L_f1_428056:\n"
"pop.w {r0, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
"movs r0, r0\n"
".word 0xC3888000\n"
".word 0x42480000\n"
".word 0x447A0000\n");
#else
    /* Host twin. tab_in models the trim table at 0x20026BA0 as
     * words (tab_in[i] == word at table + 4*i); the caller keeps
     * r0_in/r1_in in range. mem_in carries the 15 absolute-word
     * cells; calls_in counts callee invocations. */
    {
        open_cfw_bl006_spot_u32 r4 = r0_in;
        open_cfw_bl006_spot_u32 r5 = r2_in;
        open_cfw_bl006_spot_u32 r6 = 0U;
        open_cfw_bl006_spot_u32 w4 = tab_in[r0_in + 1U];
        open_cfw_bl006_spot_u32 sb = (w4 >> 21U) & 0x7FU;
        open_cfw_bl006_spot_u32 sl = w4 & 0x7FU;
        open_cfw_bl006_spot_u32 r8 =
            ((open_cfw_bl006_spot_u32)((const unsigned char *)tab_in)
                [4U * r1_in + 4U]) & 0x7FU;
        if ((mem_in->w[OPEN_CFW_BL006_SPOT_GATE] & 1U) != 0U) {
            if (r4 == mem_in->w[OPEN_CFW_BL006_SPOT_TRIMID]) {
                calls_in->ton_calls++;
                calls_in->ton_a0 = r5;
                calls_in->ton_a1 = r4;
                mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] =
                    sb | (mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] & ~0x7FU);
                calls_in->finalize_calls++;
                mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_55A] =
                    (mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_55A] & ~0xFF0000U) | 0x1A0000U;
                return 0U;
            }
            if ((mem_in->w[OPEN_CFW_BL006_SPOT_GATE] & 1U) != 0U) {
                open_cfw_bl006_spot_u32 fp = 0U;
                while (fp < 60U &&
                       ((mem_in->w[OPEN_CFW_BL006_SPOT_POLL] >> 30U) & 1U) == 0U) {
                    calls_in->delay_calls++;
                    calls_in->delay_last = 1U;
                    fp++;
                }
                calls_in->timer_calls++;
            }
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C0] = r5;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C4] = r4;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B8] = (w4 >> 7U) & 0x3FFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_BC] = (w4 >> 17U) & 0xFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B0] = sb;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B4] = sl;
        calls_in->ton_calls++;
        calls_in->ton_a0 = r5;
        calls_in->ton_a1 = r4;
        {
            open_cfw_bl006_spot_u32 d = sl - r8;
            /* `cmp d, #1; blt` is signed: q is 0 unless d >= 1. */
            open_cfw_bl006_spot_u32 q =
                ((d == 0U) || (d & 0x80000000U)) ? 0U : (d << 1U);
            open_cfw_bl006_spot_u32 s = q + r8;
            if (s >= 0x80U) {
                mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] |= 0x7FU;
            } else {
                mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] =
                    (mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] & ~0x7FU) | (s & 0x7FU);
            }
        }
        calls_in->delay_calls++;
        calls_in->delay_last = 50U;
        mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] =
            sl | (mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] & ~0x7FU);
        if (((mem_in->w[OPEN_CFW_BL006_SPOT_SYSTICK] >> 17U) & 1U) != 0U) {
            calls_in->pause_calls++;
            r6 = 1U;
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_PWR37C] |= 0x10000U;
        mem_in->w[OPEN_CFW_BL006_SPOT_PWR37C] |= 0x2000000U;
        calls_in->delay_calls++;
        calls_in->delay_last = 20U;
        if ((r6 & 0xFFU) != 0U) {
            calls_in->resume_calls++;
        }
        {
            open_cfw_bl006_spot_u32 t = mem_in->w[OPEN_CFW_BL006_SPOT_PWR280];
            mem_in->w[OPEN_CFW_BL006_SPOT_PWR280] =
                (t & ~(0xFU << 10U)) | (((w4 >> 17U) & 0xFU) << 10U);
            t = mem_in->w[OPEN_CFW_BL006_SPOT_PWR280];
            mem_in->w[OPEN_CFW_BL006_SPOT_PWR280] =
                ((w4 >> 7U) & 0x3FFU) | (t & ~0x3FFU);
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] =
            sb | (mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] & ~0x7FU);
        return 0U;
    }
#endif
}

/* Leaf F2: trim-search variant B (472 B; ends exactly at its
 * return). */
OPEN_CFW_BL006_SPOT_ATTR
open_cfw_bl006_spot_u32 open_cfw_bootloader_spot_trim_search_b_428068(
    open_cfw_bl006_spot_u32 r0_in, open_cfw_bl006_spot_u32 r1_in,
    open_cfw_bl006_spot_u32 r2_in, const open_cfw_bl006_spot_u32 *tab_in,
    open_cfw_bl006_spot_mem *mem_in, open_cfw_bl006_spot_calls *calls_in)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
"push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n"
"movs r4, r0\n"
"mov sl, r2\n"
"movs r5, #0\n"
"ldr.w r0, [pc, #0xa04]\n"
"add.w r2, r0, r4, lsl #2\n"
"adds r2, r2, #4\n"
"str r2, [sp]\n"
"add.w r2, r0, r1, lsl #2\n"
"adds r2, r2, #4\n"
"adds.w r3, r0, #0x64\n"
"ldrb r0, [r3]\n"
"ands r0, r0, #0x7f\n"
"strb.w r0, [sp, #4]\n"
"add r0, sp, #4\n"
"ldr r6, [r3]\n"
"lsrs r6, r6, #7\n"
"ands r6, r6, #0x7f\n"
"strb r6, [r0, #1]\n"
"ldr r6, [r3]\n"
"lsrs r6, r6, #0xe\n"
"ands r6, r6, #0x7f\n"
"strb r6, [r0, #2]\n"
"ldr r3, [r3]\n"
"lsrs r3, r3, #0x15\n"
"ands r3, r3, #0x7f\n"
"strb r3, [r0, #3]\n"
"ldrb r6, [r2]\n"
"ands r6, r6, #0x7f\n"
"ldr r2, [r2]\n"
"ubfx r7, r2, #0x15, #7\n"
"ldr r2, [sp]\n"
"ldr r2, [r2]\n"
"ubfx r8, r2, #0x15, #7\n"
"ldr r2, [sp]\n"
"ldrb.w sb, [r2]\n"
"ands sb, sb, #0x7f\n"
"ands r1, r1, #3\n"
"ldrb r1, [r0, r1]\n"
"ands r1, r4, #3\n"
"ldrb r0, [r0, r1]\n"
"ldr.w r0, [pc, #0x99c]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #0x1f\n"
"bpl L_f2_42810a\n"
"movs.w fp, #0\n"
"b L_f2_4280f6\n"
"L_f2_4280ec:\n"
"movs r0, #1\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"adds.w fp, fp, #1\n"
"L_f2_4280f6:\n"
"cmp.w fp, #0x3c\n"
"bhs L_f2_428106\n"
"ldr.w r0, [pc, #0x984]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #1\n"
"bpl L_f2_4280ec\n"
"L_f2_428106:\n"
"bl open_cfw_bootloader_spotmgr_timer_irq_service_42a04a\n"
"L_f2_42810a:\n"
"mov r0, sl\n"
"ldr.w r1, [pc, #0x978]\n"
"str r0, [r1]\n"
"ldr.w r1, [pc, #0x978]\n"
"str r4, [r1]\n"
"ldr r1, [sp]\n"
"ldr r1, [r1]\n"
"ubfx r1, r1, #7, #0xa\n"
"ldr.w r2, [pc, #0xb6c]\n"
"str r1, [r2]\n"
"ldr r1, [sp]\n"
"ldr r1, [r1]\n"
"ubfx r1, r1, #0x11, #4\n"
"ldr.w r2, [pc, #0xb64]\n"
"str r1, [r2]\n"
"ldr.w r1, [pc, #0xb60]\n"
"str.w r8, [r1]\n"
"ldr.w r1, [pc, #0x950]\n"
"str.w sb, [r1]\n"
"movs r1, r4\n"
"bl open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc\n"
"subs.w r0, sb, r6\n"
"cmp r0, #1\n"
"blt L_f2_428156\n"
"lsls r0, r0, #1\n"
"b L_f2_428158\n"
"L_f2_428156:\n"
"movs r0, #0\n"
"L_f2_428158:\n"
"adds r1, r0, r6\n"
"cmp r1, #0x80\n"
"blo L_f2_42816c\n"
"ldr.w r0, [pc, #0xa48]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x7f\n"
"str r1, [r0]\n"
"b L_f2_42817a\n"
"L_f2_42816c:\n"
"ldr.w r1, [pc, #0xa38]\n"
"adds r6, r0, r6\n"
"ldr r0, [r1]\n"
"bfi r0, r6, #0, #7\n"
"str r0, [r1]\n"
"L_f2_42817a:\n"
"subs.w r0, r8, r7\n"
"cmp r0, #1\n"
"blt L_f2_428186\n"
"lsls r0, r0, #1\n"
"b L_f2_428188\n"
"L_f2_428186:\n"
"movs r0, #0\n"
"L_f2_428188:\n"
"adds r1, r0, r7\n"
"cmp r1, #0x80\n"
"blo L_f2_42819c\n"
"ldr.w r0, [pc, #0xaf4]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x7f\n"
"str r1, [r0]\n"
"b L_f2_4281aa\n"
"L_f2_42819c:\n"
"ldr.w r1, [pc, #0xae4]\n"
"adds r7, r0, r7\n"
"ldr r0, [r1]\n"
"bfi r0, r7, #0, #7\n"
"str r0, [r1]\n"
"L_f2_4281aa:\n"
"movs r0, #0x32\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"ldr.w r0, [pc, #0xad0]\n"
"ldr r1, [r0]\n"
"lsrs r1, r1, #7\n"
"lsls r1, r1, #7\n"
"orrs.w r8, r8, r1\n"
"str.w r8, [r0]\n"
"ldr r0, [sp]\n"
"ldr r0, [r0]\n"
"ubfx r0, r0, #0x11, #4\n"
"ldr.w r1, [pc, #0xad4]\n"
"ldr r2, [r1]\n"
"bfi r2, r0, #0xa, #4\n"
"str r2, [r1]\n"
"ldr r0, [sp]\n"
"ldr r0, [r0]\n"
"ubfx r0, r0, #7, #0xa\n"
"ldr r2, [r1]\n"
"lsrs r2, r2, #0xa\n"
"lsls r2, r2, #0xa\n"
"orrs r0, r2\n"
"str r0, [r1]\n"
"movs r0, #5\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"ldr.w r0, [pc, #0x9b8]\n"
"ldr r1, [r0]\n"
"lsrs r1, r1, #7\n"
"lsls r1, r1, #7\n"
"orrs.w sb, sb, r1\n"
"str.w sb, [r0]\n"
"ldr.w r0, [pc, #0x9a8]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #0xe\n"
"bpl L_f2_428210\n"
"bl open_cfw_bootloader_spotmgr_irq_pause_41e22e\n"
"movs r5, #1\n"
"L_f2_428210:\n"
"ldr.w r0, [pc, #0xa88]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x10000\n"
"str r1, [r0]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #8\n"
"str r1, [r0]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x40\n"
"str r1, [r0]\n"
"movs r0, #0x14\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"uxtb r5, r5\n"
"cmp r5, #0\n"
"beq L_f2_42823c\n"
"bl open_cfw_bootloader_spotmgr_irq_resume_41e1e8\n"
"L_f2_42823c:\n"
"pop.w {r0, r1, r2, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n");
#else
    /* Host twin. r2_in arrives in sl (published to SRAM_C0 and
     * reloaded into r0 before ton-adjust, so ton-adjust always
     * receives (sl, r4) on every path). */
    {
        open_cfw_bl006_spot_u32 r4 = r0_in;
        open_cfw_bl006_spot_u32 sl_arg = r2_in;
        open_cfw_bl006_spot_u32 r5 = 0U;
        open_cfw_bl006_spot_u32 sav = tab_in[r0_in + 1U];
        open_cfw_bl006_spot_u32 w1 = tab_in[r1_in + 1U];
        open_cfw_bl006_spot_u32 r6 = w1 & 0x7FU;
        open_cfw_bl006_spot_u32 r7 = (w1 >> 21U) & 0x7FU;
        open_cfw_bl006_spot_u32 r8 = (sav >> 21U) & 0x7FU;
        open_cfw_bl006_spot_u32 sb = sav & 0x7FU;
        if ((mem_in->w[OPEN_CFW_BL006_SPOT_GATE] & 1U) != 0U) {
            open_cfw_bl006_spot_u32 fp = 0U;
            while (fp < 60U &&
                   ((mem_in->w[OPEN_CFW_BL006_SPOT_POLL] >> 30U) & 1U) == 0U) {
                calls_in->delay_calls++;
                calls_in->delay_last = 1U;
                fp++;
            }
            calls_in->timer_calls++;
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C0] = sl_arg;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C4] = r4;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B8] = (sav >> 7U) & 0x3FFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_BC] = (sav >> 17U) & 0xFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B0] = r8;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B4] = sb;
        calls_in->ton_calls++;
        calls_in->ton_a0 = sl_arg;
        calls_in->ton_a1 = r4;
        {
            open_cfw_bl006_spot_u32 d = sb - r6;
            /* `cmp d, #1; blt` is signed: q is 0 unless d >= 1. */
            open_cfw_bl006_spot_u32 q =
                ((d == 0U) || (d & 0x80000000U)) ? 0U : (d << 1U);
            open_cfw_bl006_spot_u32 s = q + r6;
            if (s >= 0x80U) {
                mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] |= 0x7FU;
            } else {
                mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] =
                    (mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] & ~0x7FU) | (s & 0x7FU);
            }
        }
        {
            open_cfw_bl006_spot_u32 d = r8 - r7;
            /* `cmp d, #1; blt` is signed: q is 0 unless d >= 1. */
            open_cfw_bl006_spot_u32 q =
                ((d == 0U) || (d & 0x80000000U)) ? 0U : (d << 1U);
            open_cfw_bl006_spot_u32 s = q + r7;
            if (s >= 0x80U) {
                mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] |= 0x7FU;
            } else {
                mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] =
                    (mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] & ~0x7FU) | (s & 0x7FU);
            }
        }
        calls_in->delay_calls++;
        calls_in->delay_last = 50U;
        mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] =
            r8 | (mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] & ~0x7FU);
        {
            open_cfw_bl006_spot_u32 t = mem_in->w[OPEN_CFW_BL006_SPOT_PWR280];
            mem_in->w[OPEN_CFW_BL006_SPOT_PWR280] =
                (t & ~(0xFU << 10U)) | (((sav >> 17U) & 0xFU) << 10U);
            t = mem_in->w[OPEN_CFW_BL006_SPOT_PWR280];
            mem_in->w[OPEN_CFW_BL006_SPOT_PWR280] =
                ((sav >> 7U) & 0x3FFU) | (t & ~0x3FFU);
        }
        calls_in->delay_calls++;
        calls_in->delay_last = 5U;
        mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] =
            sb | (mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] & ~0x7FU);
        if (((mem_in->w[OPEN_CFW_BL006_SPOT_SYSTICK] >> 17U) & 1U) != 0U) {
            calls_in->pause_calls++;
            r5 = 1U;
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_PWR37C] |= 0x10000U;
        mem_in->w[OPEN_CFW_BL006_SPOT_PWR37C] |= 8U;
        mem_in->w[OPEN_CFW_BL006_SPOT_PWR37C] |= 0x40U;
        calls_in->delay_calls++;
        calls_in->delay_last = 20U;
        if ((r5 & 0xFFU) != 0U) {
            calls_in->resume_calls++;
        }
        return 0U;
    }
#endif
}

/* Leaf F3: trim-search variant C (312 B; ends exactly at its
 * return). */
OPEN_CFW_BL006_SPOT_ATTR
open_cfw_bl006_spot_u32 open_cfw_bootloader_spot_trim_search_c_428240(
    open_cfw_bl006_spot_u32 r0_in, open_cfw_bl006_spot_u32 r1_in,
    open_cfw_bl006_spot_u32 r2_in, const open_cfw_bl006_spot_u32 *tab_in,
    open_cfw_bl006_spot_mem *mem_in, open_cfw_bl006_spot_calls *calls_in)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
"push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n"
"movs r4, r0\n"
"mov sl, r2\n"
"movs r0, #0\n"
"ldr.w r5, [pc, #0x82c]\n"
"add.w r0, r5, r4, lsl #2\n"
"adds r6, r0, #4\n"
"add.w r0, r5, r1, lsl #2\n"
"adds r2, r0, #4\n"
"adds.w r3, r5, #0x64\n"
"ldrb r0, [r3]\n"
"ands r0, r0, #0x7f\n"
"strb.w r0, [sp]\n"
"mov r0, sp\n"
"ldr r7, [r3]\n"
"lsrs r7, r7, #7\n"
"ands r7, r7, #0x7f\n"
"strb r7, [r0, #1]\n"
"ldr r7, [r3]\n"
"lsrs r7, r7, #0xe\n"
"ands r7, r7, #0x7f\n"
"strb r7, [r0, #2]\n"
"ldr r3, [r3]\n"
"lsrs r3, r3, #0x15\n"
"ands r3, r3, #0x7f\n"
"strb r3, [r0, #3]\n"
"ldrb r3, [r2]\n"
"ands r3, r3, #0x7f\n"
"ldr r2, [r2]\n"
"ubfx r7, r2, #0x15, #7\n"
"ldr r2, [r6]\n"
"ubfx r8, r2, #0x15, #7\n"
"ldrb.w sb, [r6]\n"
"ands sb, sb, #0x7f\n"
"ands r1, r1, #3\n"
"ldrb r1, [r0, r1]\n"
"ands r1, r4, #3\n"
"ldrb r0, [r0, r1]\n"
"ldr.w r0, [pc, #0x7cc]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #0x1f\n"
"bpl L_f3_4282dc\n"
"movs.w fp, #0\n"
"b L_f3_4282c8\n"
"L_f3_4282be:\n"
"movs r0, #1\n"
"bl open_cfw_bootloader_retained_delay_41d1c0\n"
"adds.w fp, fp, #1\n"
"L_f3_4282c8:\n"
"cmp.w fp, #0x3c\n"
"bhs L_f3_4282d8\n"
"ldr.w r0, [pc, #0x7b4]\n"
"ldr r0, [r0]\n"
"lsls r0, r0, #1\n"
"bpl L_f3_4282be\n"
"L_f3_4282d8:\n"
"bl open_cfw_bootloader_spotmgr_timer_irq_service_42a04a\n"
"L_f3_4282dc:\n"
"mov r0, sl\n"
"ldr.w r1, [pc, #0x7a8]\n"
"str r0, [r1]\n"
"ldr.w r1, [pc, #0x7a4]\n"
"str r4, [r1]\n"
"ldr r1, [r6]\n"
"ubfx r1, r1, #7, #0xa\n"
"ldr.w r2, [pc, #0x99c]\n"
"str r1, [r2]\n"
"ldr r1, [r6]\n"
"ubfx r1, r1, #0x11, #4\n"
"ldr.w r2, [pc, #0x994]\n"
"str r1, [r2]\n"
"ldr.w r1, [pc, #0x994]\n"
"str.w r8, [r1]\n"
"ldr.w r1, [pc, #0x784]\n"
"str.w sb, [r1]\n"
"movs r1, r4\n"
"bl open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc\n"
"ldr.w r0, [pc, #0x88c]\n"
"ldr r1, [r5, #0x50]\n"
"ldr r2, [r0]\n"
"bfi r2, r1, #0, #7\n"
"str r2, [r0]\n"
"subs.w r8, r8, r7\n"
"cmp.w r8, #1\n"
"blt L_f3_428336\n"
"lsls.w r8, r8, #1\n"
"b L_f3_42833a\n"
"L_f3_428336:\n"
"movs.w r8, #0\n"
"L_f3_42833a:\n"
"adds.w r0, r8, r7\n"
"cmp r0, #0x80\n"
"blo L_f3_428350\n"
"ldr.w r0, [pc, #0x940]\n"
"ldr r1, [r0]\n"
"orrs r1, r1, #0x7f\n"
"str r1, [r0]\n"
"b L_f3_428360\n"
"L_f3_428350:\n"
"ldr.w r0, [pc, #0x930]\n"
"adds.w r7, r8, r7\n"
"ldr r1, [r0]\n"
"bfi r1, r7, #0, #7\n"
"str r1, [r0]\n"
"L_f3_428360:\n"
"ldr.w r0, [pc, #0x71c]\n"
"str r4, [r0]\n"
"movs r0, #0x32\n"
"bl open_cfw_bootloader_spotmgr_transition_start_41cc48\n"
"movs r0, #2\n"
"ldr.w r1, [pc, #0x918]\n"
"strb r0, [r1]\n"
"pop.w {r0, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n");
#else
    /* Host twin. r5 is the table base (pool word); the word at
     * table + 0x50 feeds the pulse-register merge. transition_start
     * receives 50 in r0; there is no delay(50) in this variant. */
    {
        open_cfw_bl006_spot_u32 r4 = r0_in;
        open_cfw_bl006_spot_u32 sl_arg = r2_in;
        open_cfw_bl006_spot_u32 w6 = tab_in[r0_in + 1U];
        open_cfw_bl006_spot_u32 w2 = tab_in[r1_in + 1U];
        open_cfw_bl006_spot_u32 r7 = (w2 >> 21U) & 0x7FU;
        open_cfw_bl006_spot_u32 r8 = (w6 >> 21U) & 0x7FU;
        open_cfw_bl006_spot_u32 sb = w6 & 0x7FU;
        if ((mem_in->w[OPEN_CFW_BL006_SPOT_GATE] & 1U) != 0U) {
            open_cfw_bl006_spot_u32 fp = 0U;
            while (fp < 60U &&
                   ((mem_in->w[OPEN_CFW_BL006_SPOT_POLL] >> 30U) & 1U) == 0U) {
                calls_in->delay_calls++;
                calls_in->delay_last = 1U;
                fp++;
            }
            calls_in->timer_calls++;
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C0] = sl_arg;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_C4] = r4;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B8] = (w6 >> 7U) & 0x3FFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_BC] = (w6 >> 17U) & 0xFU;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B0] = r8;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_B4] = sb;
        calls_in->ton_calls++;
        calls_in->ton_a0 = sl_arg;
        calls_in->ton_a1 = r4;
        {
            open_cfw_bl006_spot_u32 t50 = tab_in[0x50U / 4U];
            mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] =
                (mem_in->w[OPEN_CFW_BL006_SPOT_PULSE4C] & ~0x7FU) | (t50 & 0x7FU);
        }
        {
            open_cfw_bl006_spot_u32 d = r8 - r7;
            /* `cmp d, #1; blt` is signed: q is 0 unless d >= 1. */
            open_cfw_bl006_spot_u32 q =
                ((d == 0U) || (d & 0x80000000U)) ? 0U : (d << 1U);
            open_cfw_bl006_spot_u32 s = q + r7;
            if (s >= 0x80U) {
                mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] |= 0x7FU;
            } else {
                mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] =
                    (mem_in->w[OPEN_CFW_BL006_SPOT_CTRL44] & ~0x7FU) | (s & 0x7FU);
            }
        }
        mem_in->w[OPEN_CFW_BL006_SPOT_TRIMID] = r4;
        calls_in->transstart_calls++;
        calls_in->transstart_arg = 50U;
        mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_55A] =
            (mem_in->w[OPEN_CFW_BL006_SPOT_SRAM_55A] & ~0xFF0000U) | 0x020000U;
        return 0U;
    }
#endif
}
