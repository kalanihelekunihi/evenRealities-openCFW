/* AmbiqSuite Apollo510 HAL, mcu/apollo510/hal/am_hal_spotmgr.c (BSD-3-Clause, Ambiq Micro).
 * Stock-variant reconstruction of am_hal_spotmgr_init, native 0x480434..0x4806d0.
 *
 * The stock body differs from the pinned SDK 5.1.0 text (ambiqhal_ambiq 5efc0228):
 *  - g_bCallPcm2p0Spotmgr is evaluated inline, not stored;
 *  - when PCM1.0/1.1, PCM2.0 or PCM2.1-without-UCRG-patch trims are present it
 *    first sets MCUCTRL 0x40020028 bit0 (clearing bit1) and 0x40020060 bits 15/14/13;
 *  - the PCM2.2 table has no simobuck_init_bfr_ovr, and the PCM2.1 table installs
 *    the boost-timer service (+0x2c) but no post_lptohp handler (+0x28);
 *  - state is 0x3c bytes: NO_TEMPSENSE_IN_DEEPSLEEP=0, AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH=1.
 * Revision word: MCUCTRL CHIPREV low byte 0x21=B0, 0x22=B1, 0x23=B2; trim = g_ui32TrimVer. */
#include <stdint.h>

typedef uint32_t (*g2_spotmgr_fn)(void);

/* am_hal_spotmgr_state_t as linked in stock (RAM 0x20073270, 0x3c bytes). */
typedef struct {
    g2_spotmgr_fn init;                       /* +0x00 */
    g2_spotmgr_fn power_state_update;         /* +0x04 (eStimulus, bOn, pArgs) */
    g2_spotmgr_fn default_reset;              /* +0x08 */
    g2_spotmgr_fn tempco_postpone_set;        /* +0x0c */
    g2_spotmgr_fn tempco_pending_handle;      /* +0x10 */
    g2_spotmgr_fn simobuck_init_bfr_ovr;      /* +0x14 */
    g2_spotmgr_fn simobuck_init_bfr_enable;   /* +0x18 */
    g2_spotmgr_fn simobuck_init_aft_enable;   /* +0x1c */
    g2_spotmgr_fn ton_config_init;            /* +0x20 */
    g2_spotmgr_fn ton_config_update;          /* +0x24 (bGpuOn, eGpuSt) */
    g2_spotmgr_fn post_lptohp_handle;         /* +0x28 */
    g2_spotmgr_fn timer_interrupt_service;    /* +0x2c */
    g2_spotmgr_fn simobuck_lp_autosw_init;    /* +0x30 */
    g2_spotmgr_fn simobuck_lp_autosw_enable;  /* +0x34 */
    g2_spotmgr_fn simobuck_lp_autosw_disable; /* +0x38 */
} g2_spotmgr_state_t;
_Static_assert(sizeof(g2_spotmgr_state_t) == 0x3cu, "stock memset length");

extern g2_spotmgr_state_t g2_spotmgr_state;      /* RAM 0x20073270 (audio_ble_flash_callbacks elsewhere) */
extern volatile uint32_t g2_pwrctrl_trim_version; /* RAM 0x200001e8, g_ui32TrimVer */
extern volatile uint8_t g2_spotmgr_is_pcm2p1;          /* RAM 0x20074f64 */
extern volatile uint8_t g2_spotmgr_is_pcm1p0_or_1p1;   /* RAM 0x20074f65 */
extern volatile uint8_t g2_spotmgr_is_b0_pcm1p1_newer; /* RAM 0x20074f66 */
extern volatile uint8_t g2_spotmgr_is_pcm2p0;          /* RAM 0x20074f67 */
extern volatile uint8_t g2_spotmgr_is_pcm2p2_newer;    /* RAM 0x20074f68 */
extern volatile uint8_t g2_spotmgr_is_pcm2p1_wo_patch; /* RAM 0x20074f69 */
/* g_sINFO1regs (RAM 0x20071948); +0x34 is ui32PATCH_TRACKER0. */
extern volatile uint8_t g2_pwrctrl_info1_regs[0x80];

#define G2_MCUCTRL_CHIPREV (*(volatile uint32_t *)(uintptr_t)0x4002000cu)
#define G2_MCUCTRL_REG28   (*(volatile uint32_t *)(uintptr_t)0x40020028u)
#define G2_MCUCTRL_REG60   (*(volatile uint32_t *)(uintptr_t)0x40020060u)

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */

/* PCM-specific SPOT manager implementations (native addresses, Thumb bit clear). */
extern uint32_t spotmgr_pcm2_2_init_5a4d48(void);
extern uint32_t spotmgr_pcm2_2_power_state_update_5a490c(void);
extern uint32_t spotmgr_pcm2_2_default_reset_5a4e0c(void);
extern uint32_t spotmgr_pcm2_2_simobuck_init_aft_enable_5a4d00(void);
extern uint32_t spotmgr_pcm2_2_post_lptohp_handle_5a40b6(void);
extern uint32_t spotmgr_pcm2_2_boost_timer_interrupt_service_5a40ca(void);
extern uint32_t spotmgr_pcm2_1_init_5a1c18(void);
extern uint32_t spotmgr_pcm2_1_power_state_update_5a1738(void);
extern uint32_t spotmgr_pcm2_1_default_reset_5a1da4(void);
extern uint32_t spotmgr_pcm2_1_simobuck_init_bfr_ovr_5a1bbc(void);
extern uint32_t spotmgr_pcm2_1_simobuck_init_bfr_enable_5a1bcc(void);
extern uint32_t spotmgr_pcm2_1_simobuck_init_aft_enable_5a1bec(void);
extern uint32_t spotmgr_pcm2_1_boost_timer_interrupt_service_5a0bcc(void);
extern uint32_t spotmgr_pcm2_0_init_5a08e4(void);
extern uint32_t spotmgr_pcm2_0_power_state_update_5a0786(void);
extern uint32_t spotmgr_pcm2_0_default_reset_5a0a6c(void);
extern uint32_t spotmgr_pcm2_0_tempco_postpone_5a07e6(void);
extern uint32_t spotmgr_pcm2_0_tempco_pending_handle_5a07f0(void);
extern uint32_t spotmgr_pcm2_0_simobuck_lp_autosw_init_5a085e(void);
extern uint32_t spotmgr_pcm2_0_simobuck_lp_autosw_enable_5a08b6(void);
extern uint32_t spotmgr_pcm2_0_simobuck_lp_autosw_disable_5a08ca(void);
extern uint32_t spotmgr_pcm2_0_simobuck_init_bfr_enable_5a081c(void);
extern uint32_t spotmgr_pcm2_0_simobuck_init_aft_enable_5a0842(void);
extern uint32_t spotmgr_pcm0_7_init_5a0018(void);
extern uint32_t spotmgr_pcm0_7_power_state_update_59fd36(void);
extern uint32_t spotmgr_pcm0_7_simobuck_init_bfr_enable_59fd82(void);
extern uint32_t spotmgr_pcm0_7_simobuck_init_aft_enable_59fda8(void);
extern uint32_t spotmgr_pcm0_7_ton_config_init_59fdc2(void);
extern uint32_t spotmgr_pcm0_7_ton_config_update_59fe5a(void);

#define REV()  (G2_MCUCTRL_CHIPREV & 0xffu)
#define TRIM() (g2_pwrctrl_trim_version)
#define FN(f)  ((g2_spotmgr_fn)(f))

uint32_t am_hal_spotmgr_init_480434(void)
{
    uint32_t status = 0u;
    g2_spotmgr_state_t *s = &g2_spotmgr_state;

    audio_uart_buffer_zero(s, sizeof *s, 0u);

    g2_spotmgr_is_pcm2p2_newer = ((REV() == 0x23u && TRIM() >= 2u) || REV() >= 0x24u) ? 1u : 0u;
    g2_spotmgr_is_pcm2p1 = ((REV() == 0x22u && TRIM() == 2u) ||
                            (REV() == 0x23u && TRIM() == 1u)) ? 1u : 0u;
    g2_spotmgr_is_pcm1p0_or_1p1 = ((REV() == 0x21u && TRIM() == 2u) ||
                                   (REV() == 0x21u && TRIM() == 3u) ||
                                   (REV() == 0x22u && TRIM() == 0u)) ? 1u : 0u;
    g2_spotmgr_is_b0_pcm1p1_newer = (REV() == 0x21u && TRIM() >= 3u) ? 1u : 0u;
    g2_spotmgr_is_pcm2p0 = ((REV() == 0x22u && TRIM() == 1u) ||
                            (REV() == 0x23u && TRIM() == 0u)) ? 1u : 0u;
    if ((REV() == 0x22u && TRIM() == 2u) || (REV() == 0x23u && TRIM() == 1u))
        g2_spotmgr_is_pcm2p1_wo_patch = (uint8_t)((g2_pwrctrl_info1_regs[0x34] & 1u) ^ 1u);
    else
        g2_spotmgr_is_pcm2p1_wo_patch = 0u;

    if ((uint8_t)(g2_spotmgr_is_pcm1p0_or_1p1 | g2_spotmgr_is_pcm2p0 |
                  g2_spotmgr_is_pcm2p1_wo_patch) != 0u) {
        G2_MCUCTRL_REG28 &= ~2u;
        G2_MCUCTRL_REG28 |= 1u;
        G2_MCUCTRL_REG60 |= 0x8000u;
        G2_MCUCTRL_REG60 |= 0x4000u;
        G2_MCUCTRL_REG60 |= 0x2000u;
    }

    if (g2_spotmgr_is_pcm2p2_newer != 0u) {
        s->init = FN(spotmgr_pcm2_2_init_5a4d48);
        s->power_state_update = FN(spotmgr_pcm2_2_power_state_update_5a490c);
        s->default_reset = FN(spotmgr_pcm2_2_default_reset_5a4e0c);
        s->simobuck_init_aft_enable = FN(spotmgr_pcm2_2_simobuck_init_aft_enable_5a4d00);
        s->post_lptohp_handle = FN(spotmgr_pcm2_2_post_lptohp_handle_5a40b6);
        s->timer_interrupt_service = FN(spotmgr_pcm2_2_boost_timer_interrupt_service_5a40ca);
    } else if (g2_spotmgr_is_pcm2p1 != 0u) {
        s->init = FN(spotmgr_pcm2_1_init_5a1c18);
        s->power_state_update = FN(spotmgr_pcm2_1_power_state_update_5a1738);
        s->default_reset = FN(spotmgr_pcm2_1_default_reset_5a1da4);
        s->simobuck_init_bfr_ovr = FN(spotmgr_pcm2_1_simobuck_init_bfr_ovr_5a1bbc);
        s->simobuck_init_bfr_enable = FN(spotmgr_pcm2_1_simobuck_init_bfr_enable_5a1bcc);
        s->simobuck_init_aft_enable = FN(spotmgr_pcm2_1_simobuck_init_aft_enable_5a1bec);
        s->timer_interrupt_service = FN(spotmgr_pcm2_1_boost_timer_interrupt_service_5a0bcc);
    } else if ((REV() == 0x21u && TRIM() >= 2u) || (REV() == 0x22u && TRIM() < 2u) ||
               (REV() == 0x23u && TRIM() == 0u)) {
        /* g_bCallPcm2p0Spotmgr */
        s->init = FN(spotmgr_pcm2_0_init_5a08e4);
        s->power_state_update = FN(spotmgr_pcm2_0_power_state_update_5a0786);
        s->default_reset = FN(spotmgr_pcm2_0_default_reset_5a0a6c);
        s->tempco_postpone_set = FN(spotmgr_pcm2_0_tempco_postpone_5a07e6);
        s->tempco_pending_handle = FN(spotmgr_pcm2_0_tempco_pending_handle_5a07f0);
        s->simobuck_lp_autosw_init = FN(spotmgr_pcm2_0_simobuck_lp_autosw_init_5a085e);
        s->simobuck_lp_autosw_enable = FN(spotmgr_pcm2_0_simobuck_lp_autosw_enable_5a08b6);
        s->simobuck_lp_autosw_disable = FN(spotmgr_pcm2_0_simobuck_lp_autosw_disable_5a08ca);
        if (REV() == 0x21u && TRIM() == 2u) { /* APOLLO5_B0_PCM1P0 */
            s->simobuck_init_bfr_enable = FN(spotmgr_pcm0_7_simobuck_init_bfr_enable_59fd82);
            s->simobuck_init_aft_enable = FN(spotmgr_pcm0_7_simobuck_init_aft_enable_59fda8);
        } else {
            s->simobuck_init_bfr_enable = FN(spotmgr_pcm2_0_simobuck_init_bfr_enable_5a081c);
            s->simobuck_init_aft_enable = FN(spotmgr_pcm2_0_simobuck_init_aft_enable_5a0842);
        }
    } else if (REV() == 0x21u && TRIM() == 1u) { /* APOLLO5_B0_PCM0P7 */
        s->init = FN(spotmgr_pcm0_7_init_5a0018);
        s->power_state_update = FN(spotmgr_pcm0_7_power_state_update_59fd36);
        s->simobuck_init_bfr_enable = FN(spotmgr_pcm0_7_simobuck_init_bfr_enable_59fd82);
        s->simobuck_init_aft_enable = FN(spotmgr_pcm0_7_simobuck_init_aft_enable_59fda8);
    }

    if (REV() == 0x21u && TRIM() < 2u) { /* APOLLO5_B0_LE_PCM0P7 */
        s->ton_config_init = FN(spotmgr_pcm0_7_ton_config_init_59fdc2);
        s->ton_config_update = FN(spotmgr_pcm0_7_ton_config_update_59fe5a);
    }

    if (s->init != 0)
        status = s->init();
    return status;
}
