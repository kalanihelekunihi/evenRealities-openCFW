/* Storage owned by the hand-written stock-variant HAL units (S1
 * storage-definition pass, 2.2.6.10).
 *
 * The AmbiqSuite files below declare these objects static; the stock Apollo
 * main image is linked from older/variant revisions that this tree
 * reconstructs by hand (hal/a-12-stimer, hal/a-03-sysctrl), so no upstream unit defines them. If a later segment
 * builds one of those files from the pinned upstream (or a generated patch of
 * it), retire the matching block here.
 *
 * Public AmbiqSuite globals (g_ui32TrimVer, g_sINFO1regs, g_eCurMcuPwrMode,
 * g_bOrigTrimsStored, g_orig_*, g_bFrcBuckAct, g_bIsPCM*, g_sSpotMgr,
 * am_hal_gpio_pincfg_*) are library-owned and are NOT defined here.
 *
 * .data values are from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4); ROM bytes are from ota_s200_firmware_ota.bin. */
#include <stdbool.h>
#include <stdint.h>

/* ---- am_hal_stimer.c (older variant, no AM_CRITICAL) -------------------- */

volatile bool g2_stimer_configured_20074f7a; /* RAM 0x20074f7a, g_bStimerConfigured */

/* RAM 0x20000318 (.data): g_ui32LastStimer, eight words 0xfffffffe. */
uint32_t g2_stimer_last_compare_20000318[8] = {
    0xfffffffeu, 0xfffffffeu, 0xfffffffeu, 0xfffffffeu,
    0xfffffffeu, 0xfffffffeu, 0xfffffffeu, 0xfffffffeu,
};

/* ---- am_hal_spotmgr*.c ---------------------------------------------------
 * Retired 2026-10-30: SPOTMGR is the upstream SDK 5.0.0 + 66185cb text
 * ({gen}/ambiqhal-apollo510-boot/am_hal_spotmgr*.c), which defines its own
 * statics (TON trims, PCM2.0 flags, trim snapshots). */

/* ---- am_hal_sysctrl.c sleep variant ------------------------------------- */

/* ROM 0x78ee5c: copy-initialiser of the deep-sleep CPDLP word,
 * bytes 00 02 02 00 = {RLP 0, ELP retain, CLP retain, 0}. */
const uint32_t g2_sysctrl_ds_cpdlp_template = 0x00020200u;
