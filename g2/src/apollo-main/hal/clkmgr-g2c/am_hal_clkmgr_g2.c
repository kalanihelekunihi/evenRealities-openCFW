// SPDX-License-Identifier: BSD-3-Clause
/*
 * Stock-derived am_hal_clkmgr entries that the hand copy (hal/clock/...) does not
 * already export. Wave22: the upstream am_hal_clkmgr.c include is gone. Of its
 * globals, the composed image referenced only clock_request/release (hand copy),
 * clock_release_all (mspi) and the four private_clkgen_* helpers (upstream
 * am_hal_clkgen.c control cases 2..5). All of those are now stock bodies over the
 * stock RAM below.
 *
 * Stock clock-manager RAM map (wave21; literal pools of the stock clkmgr functions
 * 0x4c3750..0x4c45e2 read from /tmp/apm.bin and matched against the Ghidra decomp
 * corpus apollo-main/ghidra/open-2026-09-29 decomp/004c44bc.c etc.):
 *   g_ui32ClkMgrClkSrcBm[7][2]        0x20073324  (verified: pool 0x4c43dc, row stride 8)
 *   g_sClkMgrBoardInfo (0x14 bytes)   0x200001cc  (verified: pools 0x4c43e8/0x4c46a0;
 *                                     0x4c45e2 board_info_set copies 0x14 bytes)
 *   g_sClkMgrClkConfig_HFRC/HFRC2/SYSPLL 0x20073f30/0x20073f3c/0x20073f48
 *                                     (verified: pools 0x4c4460/0x4c44b4/0x4c4654)
 *   g_ui32ClkMgrClkCfgFreq_HFRC/HFRC2/SYSPLL 0x20074250/0x20074254/0x20074258
 *                                     (verified: pools 0x4c445c/0x4c44a8/0x4c4658)
 *   g_bClkMgrClkCfgValid_HFRC/HFRC2   0x20004536/0x20004537 (.data, verified: pools
 *                                     0x4c44a0/0x4c44b8); _SYSPLL 0x20074f55 (verified: 0x4c4674)
 *   g_pSyspllHandle                   0x2007425c  (verified: pool 0x4c469c)
 *   g_bClkStabilizing_XTAL_HS/HFRC_ADJ/HFRC2_ADJ 0x20074f56/0x20074f57/0x20074f58
 *   g_bClkStablized_HFRC_ADJ          0x20074f59
 *   g_pui32ClkStabilizingCounter_XTAL_HS/HFRC_ADJ/HFRC2_ADJ 0x20074260/0x20074264/0x20074268
 *   g_bHFRC2StartPending/g_bSYSPLLStartPending 0x20074f5a/0x20074f5b
 *                                     (verified: pools 0x4c4464..0x4c4698)
 * No EXTREFCLK stabilizing flag/counter appears in the stock pools (compiled out).
 * The hand copy (hal/clock/..., entered via system/glue/clock_public_aliases.c) already
 * uses exactly these stock addresses, so it is the stock state.
 *
 * Public entries: am_hal_clkmgr_clock_request/release are the hand copy
 * (audio_clock_request/release, stock 0x4c44bc/0x4c4530; system/glue/clock_public_aliases.c).
 * Wave21's claim that stock has no private_clkgen_* helpers was wrong: Ghidra corpus open-2026-09-29
 * simply has no decomp/ entries for 0x4c45fc..0x4c46b4 (checked), but
 * stock am_hal_clkgen_control (verified disasm 0x4d3628)
 * calls 0x4c45fc/0x4c465c/0x4c4668/0x4c46b4 for cases 2..5, which are those helpers.
 */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");

extern uint32_t audio_clock_user(uint32_t clock, uint32_t user);           /* stock 0x4c37a8 */
extern uint32_t audio_clock_release(uint32_t clock, uint32_t user);        /* stock 0x4c4530 */
extern uint32_t audio_hfrc_config(uint32_t hz, const uint32_t *config);    /* stock 0x4c38a0 */
extern uint32_t audio_hfrc2_config(uint32_t hz, const uint32_t *config);   /* stock 0x4c399e */

#define CLKMGR_BOARD_XTAL_LS_FREQ (*(volatile uint32_t *)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x10u)) /* board info +0x0c */
#define HFRC_ADJ_48MHZ 48000000u      /* stock pool 0x4c46a4 = 0x2dc6c00 */
#define HFRC2_ADJ_196P608MHZ 196608000u /* stock pool 0x4c46b0 = 0xbb80000 */

/* Stock 0x4c45a4 (verified, decomp/004c45a4.c): user < 0x39 else 6; for clock 0..6,
 * release each clock this user holds; return 0. */
uint32_t am_hal_clkmgr_clock_release_all(uint32_t eUserId)
{
    uint8_t user = (uint8_t)eUserId;

    if (user >= 0x39u)
        return 6u;
    for (uint8_t clock = 0u; clock < 7u; clock++) {
        if (audio_clock_user(clock, user))
            (void)audio_clock_release(clock, user);
    }
    return 0u;
}

/* Stock 0x4c45fc (verified disasm 0x4c45fc..0x4c4650; reached from stock
 * am_hal_clkgen_control 0x4d3628 case 2): needs XTAL_LS freq (board +0x0c) else 7.
 * No args -> config_HFRC(48 MHz, NULL). Else freq = HFADJ.HFXTADJ ([8:19]) * ls,
 * snapped to 48 MHz when within one ls step below or above (pools 0x4c46a4 48 MHz,
 * 0x4c46a8 48 MHz+1, 0x4c46ac -48 MHz), then config_HFRC(freq, args). */
uint32_t am_hal_clkmgr_private_clkgen_hfadj_apply(void *pArgs)
{
    uint32_t ls = CLKMGR_BOARD_XTAL_LS_FREQ;
    uint32_t freq;

    if (ls == 0u)
        return 7u;
    if (pArgs == 0)
        return audio_hfrc_config(HFRC_ADJ_48MHZ, 0);
    freq = ((*(const uint32_t *)pArgs >> 8) & 0xfffu) * CLKMGR_BOARD_XTAL_LS_FREQ;
    if (freq < HFRC_ADJ_48MHZ) {
        if (HFRC_ADJ_48MHZ - freq < CLKMGR_BOARD_XTAL_LS_FREQ)
            freq = HFRC_ADJ_48MHZ;
    } else if (freq >= HFRC_ADJ_48MHZ + 1u &&
               freq - HFRC_ADJ_48MHZ < CLKMGR_BOARD_XTAL_LS_FREQ) {
        freq = HFRC_ADJ_48MHZ;
    }
    return audio_hfrc_config(freq, (const uint32_t *)pArgs);
}

/* Stock 0x4c465c (verified disasm; clkgen_control case 3): config_HFRC(0, NULL). */
uint32_t am_hal_clkmgr_private_clkgen_hfadj_disable(void)
{
    return audio_hfrc_config(0u, 0);
}

/* Stock 0x4c4668 (verified disasm; clkgen_control case 4): config_HFRC2(196.608 MHz, NULL). */
uint32_t am_hal_clkmgr_private_clkgen_hf2adj_apply(void)
{
    return audio_hfrc2_config(HFRC2_ADJ_196P608MHZ, 0);
}

/* Stock 0x4c46b4 (verified disasm; clkgen_control case 5): config_HFRC2(0, NULL). */
uint32_t am_hal_clkmgr_private_clkgen_hf2adj_disable(void)
{
    return audio_hfrc2_config(0u, 0);
}
