/* Storage owned by the hand-written stock-variant HAL units (S1
 * storage-definition pass, 2.2.6.10).
 *
 * The AmbiqSuite files below declare these objects static; the stock Apollo
 * main image is linked from older/variant revisions that this tree
 * reconstructs by hand (hal/a-12-stimer, hal/p-14-spotmgr pcm0_7 and pcm2_0,
 * hal/a-03-sysctrl), so no upstream unit defines them. If a later segment
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

/* ---- am_hal_spotmgr_pcm0_7.c (variant) ---------------------------------- */

volatile uint32_t g2_spotmgr_pcm0_7_cur_coreldotempcotrim_ldo; /* RAM 0x200742b4 */
volatile uint32_t g2_spotmgr_pcm0_7_cur_memldoactivetrim_ldo;  /* RAM 0x200742b8 */

/* RAM 0x2000453a..0x2000453f (.data): 0d 0d 0b 0b 12 19, the SDK defaults. */
volatile uint8_t g2_spotmgr_vddc_act_low_ton_trim = 0x0du;    /* g_ui8VddcActLowTonTrim */
volatile uint8_t g2_spotmgr_vddc_act_high_ton_trim = 0x0du;   /* g_ui8VddcActHighTonTrim */
volatile uint8_t g2_spotmgr_vddclv_act_low_ton_trim = 0x0bu;  /* g_ui8VddcLvActLowTonTrim */
volatile uint8_t g2_spotmgr_vddclv_act_high_ton_trim = 0x0bu; /* g_ui8VddcLvActHighTonTrim */
volatile uint8_t g2_spotmgr_vddf_act_low_ton_trim = 0x12u;    /* g_ui8VddfActLowTonTrim */
volatile uint8_t g2_spotmgr_vddf_act_high_ton_trim = 0x19u;   /* g_ui8VddfActHighTonTrim */

/* ROM 0x789fe0: ui8TonActiveConfig[GPU state][CPU state],
 * 01 01 02 | 01 01 02 | 01 02 02 (1 = TON level low). */
const uint8_t g2_spotmgr_ton_active_config[3][3] = {
    {0x01u, 0x01u, 0x02u},
    {0x01u, 0x01u, 0x02u},
    {0x01u, 0x02u, 0x02u},
};

/* ---- am_hal_spotmgr_pcm2_0.c (variant) ---------------------------------- */

volatile uint8_t g2_spotmgr_pcm2_0_is_b0_pcm1p0;          /* RAM 0x20074f6e, g_bIsB0Pcm1p0 */
volatile uint8_t g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1;      /* RAM 0x20074f6f, g_bIsPCM1p0Or1p1 */
volatile uint8_t g2_spotmgr_pcm2_0_is_pcm2p0_unscreened;  /* RAM 0x20074f70, g_bIsPCM2p0Unscreened */
volatile uint8_t g2_spotmgr_pcm2_0_postpone_tempco;       /* RAM 0x20074f71, g_bPostponeTempco */
volatile uint8_t g2_spotmgr_pcm2_0_tempco_pending;        /* RAM 0x20074f72, g_bTempcoPending */
volatile uint8_t g2_spotmgr_pcm2_0_tempco_range;          /* RAM 0x20074f74, g_eTempCoRange (LOW = 0) */
volatile uint32_t g2_spotmgr_pcm2_0_cur_coreldotempcotrim_ldo;  /* RAM 0x200742bc */
volatile uint32_t g2_spotmgr_pcm2_0_cur_coreldotempcotrim_buck; /* RAM 0x200742c0 */
volatile uint32_t g2_spotmgr_pcm2_0_cur_memldoactivetrim_ldo;   /* RAM 0x200742c4 */

/* ---- am_hal_sysctrl.c sleep variant ------------------------------------- */

/* ROM 0x78ee5c: copy-initialiser of the deep-sleep CPDLP word,
 * bytes 00 02 02 00 = {RLP 0, ELP retain, CLP retain, 0}. */
const uint32_t g2_sysctrl_ds_cpdlp_template = 0x00020200u;
