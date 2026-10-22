/* AmbiqSuite Apollo510 HAL, mcu/apollo510/hal/am_hal_spotmgr_pcm2_0.c (BSD-3-Clause, Ambiq Micro).
 * Stock-variant reconstruction of the PCM1.0/1.1/2.0 SPOT-manager family,
 * native 0x5a001c..0x5a0786 and 0x5a08e4..0x5a09c2 (tempco_postpone/pending,
 * simobuck_init_bfr/aft_enable, lp_autosw_* and default_reset at
 * 0x5a07e6..0x5a08e2 / 0x5a0a6c belong to other units).
 *
 * Built with AM_HAL_ENABLE_TEMPCO_VDDC=false, AM_HAL_ENABLE_TEMPCO_VDDF=true and
 * BOOST_VDDF_FOR_SDIO=false; under those settings the helper and GPU bodies
 * match the pinned SDK 5.1.0 text (ambiqhal_ambiq 5efc0228). Stock differences:
 *  - power_state_update has no STIM_INIT_STATE case and does not keep the last
 *    temperature (no fTempStatic); only CPU, GPU and TEMP stimuli act;
 *  - init only derives the three part flags: the SDK's ACRG / ANALDO writes are
 *    absent from this function;
 *  - vddc_vddf_tempco, its critical-section wrapper, tempco_update,
 *    buck_deepsleep_state_determine and both GPU sequences are out of line.
 * Floating point: tempco_update compares the temperature in single precision,
 * so this unit needs profile g2-apollo-main-3. */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define MCUCTRL_CHIPREV    REG(0x4002000cu)
#define MCUCTRL_VREFGEN2   REG(0x40020044u) /* TVRGCVREFTRIM [6:0] */
#define MCUCTRL_VREFGEN4   REG(0x4002004cu) /* TVRGFVREFTRIM [6:0] */
#define MCUCTRL_LDOREG1    REG(0x40020080u) /* CORELDOACTIVETRIM [9:0], CORELDOTEMPCOTRIM [13:10] */
#define MCUCTRL_LDOREG2    REG(0x40020088u) /* MEMLDOACTIVETRIM [5:0] */
#define MCUCTRL_D2ASPARE   REG(0x400201b0u) /* SIMOVDDCBOOST [8] */
#define MCUCTRL_SIMOBUCK2  REG(0x40020344u) /* VDDCACTLOWTONTRIM [29:25], VDDCACTHIGHTONTRIM [15:11] */
#define MCUCTRL_SIMOBUCK4  REG(0x4002034cu) /* VDDCLVACTLOWTONTRIM [29:25], VDDCLVACTHIGHTONTRIM [15:11] */
#define MCUCTRL_SIMOBUCK6  REG(0x40020354u) /* VDDFACTHIGHTONTRIM [21:17] */
#define MCUCTRL_SIMOBUCK7  REG(0x40020358u) /* VDDFACTLOWTONTRIM [12:8] */
#define MCUCTRL_PWRSW1     REG(0x40020380u) /* VDDC/VDDCLV and VDDF/VDDS short overrides [31:28] */
#define PWRCTRL_DEVPWREN   REG(0x40021004u) /* PWRENGFX [18] */
#define PWRCTRL_VRSTATUS   REG(0x40021108u) /* SIMOBUCKST [5:4], 3 = active */
#define TIMER_GLOBEN       REG(0x40008010u)
#define TIMER_CTRL0(n)     REG(0x40008200u + 0x20u * (n)) /* TMR0EN [0], TMR0CLK [16:8] */
#define STIMER_STCFG       REG(0x40008800u)               /* CLKSEL [3:0] */

#define FIELD_SET(reg, mask, shift, v) ((reg) = ((reg) & ~(uint32_t)(mask)) | (((uint32_t)(v) << (shift)) & (mask)))
#define SIMOBUCK_ACTIVE() (((PWRCTRL_VRSTATUS & 0x3fu) >> 4) == 3u)

#define TVRGFVREFTRIM_BOOST_CODE_FOR_GPU 15u
#define CORELDOTRIM_BOOST_CODE_FOR_GPU   12u
#define TVRGCVREFTRIM_BOOST_CODE_FOR_GPU 9u

#define LOW_LIMIT                  (-273.0f)
#define HIGH_LIMIT                 1000.0f
#define VDDC_VDDF_TEMPCO_THRESHOLD 35.0f
#define BUCK_LP_TEMP_THRESHOLD     50.0f
#define TEMP_HYSTERESIS            2.0f

/* am_hal_pwrctrl_tempco_range_e */
enum { TEMPCO_RANGE_LOW = 0, TEMPCO_RANGE_MID = 1, TEMPCO_RANGE_HIGH = 2, TEMPCO_OUT_OF_RANGE = 3 };
/* am_hal_spotmgr_gpu_state_e / cpu_state_e / stimulus_e values seen in stock. */
enum { GPUSTATE_OFF = 0, GPUSTATE_ACTIVE_LP = 1, GPUSTATE_ACTIVE_HP = 2 };
enum { CPUSTATE_SLEEP_DEEP = 2 };
enum { STIM_CPU_STATE = 0, STIM_GPU_STATE = 1, STIM_TEMP = 2 };

/* am_hal_spotmgr_tempco_param_t */
typedef struct {
    float temperature;  /* +0x0 */
    float range_lower;  /* +0x4 */
    float range_higher; /* +0x8 */
} g2_spotmgr_tempco_param_t;
_Static_assert(sizeof(g2_spotmgr_tempco_param_t) == 12u, "tempco ABI");

extern volatile uint32_t g2_pwrctrl_trim_version;            /* RAM 0x200001e8, g_ui32TrimVer */
extern volatile uint8_t g2_pwrctrl_info1_regs[0x80];         /* RAM 0x20071948, g_sINFO1regs; +0x44 ui32FT1_GDR1 */
extern volatile uint8_t g2_spotmgr_is_pcm2p0;                /* RAM 0x20074f67, g_bIsPCM2p0 */
extern volatile uint8_t g2_spotmgr_orig_trims_stored;        /* RAM 0x20074f63, g_bOrigTrimsStored */
extern volatile uint32_t g2_spotmgr_orig_tvrgfvreftrim;      /* RAM 0x20074270, g_orig_TVRGFVREFTRIM */
extern volatile uint8_t g2_spotmgr_frc_buck_act;             /* RAM 0x20074f7b, g_bFrcBuckAct */
extern volatile uint8_t g2_spotmgr_pcm2_0_is_b0_pcm1p0;      /* RAM 0x20074f6e, g_bIsB0Pcm1p0 */
extern volatile uint8_t g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1;  /* RAM 0x20074f6f, g_bIsPCM1p0Or1p1 */
extern volatile uint8_t g2_spotmgr_pcm2_0_is_pcm2p0_unscreened; /* RAM 0x20074f70, g_bIsPCM2p0Unscreened */
extern volatile uint8_t g2_spotmgr_pcm2_0_postpone_tempco;   /* RAM 0x20074f71, g_bPostponeTempco */
extern volatile uint8_t g2_spotmgr_pcm2_0_tempco_pending;    /* RAM 0x20074f72, g_bTempcoPending */
extern volatile uint8_t g2_spotmgr_pcm2_0_tempco_range;      /* RAM 0x20074f74, g_eTempCoRange */
extern volatile uint32_t g2_spotmgr_pcm2_0_cur_coreldotempcotrim_ldo;  /* RAM 0x200742bc */
extern volatile uint32_t g2_spotmgr_pcm2_0_cur_coreldotempcotrim_buck; /* RAM 0x200742c0 */
extern volatile uint32_t g2_spotmgr_pcm2_0_cur_memldoactivetrim_ldo;   /* RAM 0x200742c4 */

extern void audio_delay_us(uint32_t);                        /* am_hal_delay_us 0x4807a0 */
extern uint32_t g2_main_critical_save_473940(void);          /* AM_CRITICAL_BEGIN (PRIMASK save + cpsid) */
extern bool am_hal_stimer_is_running_48d620(void);

static inline void critical_end(uint32_t primask)
{
    __asm volatile("msr primask, %0" : : "r"(primask) : "memory");
}

/* vddc_vddf_tempco: only the VDDF trim is compensated in this build. */
void spotmgr_pcm2_0_vddc_vddf_tempco_5a001c(uint8_t range)
{
    int32_t vddf_diff = 0;
    int32_t vddf_reduce;

    if (g2_spotmgr_orig_trims_stored == 0u || !SIMOBUCK_ACTIVE())
        return;
    if ((PWRCTRL_DEVPWREN & 0x40000u) != 0u && g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 != 0u)
        vddf_diff = (int32_t)TVRGFVREFTRIM_BOOST_CODE_FOR_GPU;
    switch (range) {
    case TEMPCO_RANGE_LOW:
    case TEMPCO_RANGE_MID:
        vddf_reduce = 10;
        break;
    default:
        vddf_reduce = 0;
        break;
    }
    if (vddf_reduce - vddf_diff > 0) {
        uint32_t reduce = (uint32_t)(vddf_reduce - vddf_diff);
        uint32_t base = g2_spotmgr_orig_tvrgfvreftrim;
        FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0, base > reduce ? base - reduce : 0u);
    } else {
        uint32_t value = (uint32_t)(vddf_diff - vddf_reduce) + g2_spotmgr_orig_tvrgfvreftrim;
        FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0, value < 0x80u ? value : 0x7fu);
    }
}

/* vddc_vddf_tempco_top: applies now or defers while tempco is postponed. */
void spotmgr_pcm2_0_vddc_vddf_tempco_top_5a00c8(uint8_t range)
{
    uint32_t primask = g2_main_critical_save_473940();
    g2_spotmgr_pcm2_0_tempco_range = range;
    if (g2_spotmgr_pcm2_0_postpone_tempco != 0u)
        g2_spotmgr_pcm2_0_tempco_pending = 1u;
    else
        spotmgr_pcm2_0_vddc_vddf_tempco_5a001c(range);
    critical_end(primask);
}

/* Returns 0, or 1 (AM_HAL_STATUS_FAIL) with zero bounds when out of range. */
uint32_t spotmgr_pcm2_0_tempco_update_5a00fc(g2_spotmgr_tempco_param_t *tempco)
{
    uint8_t range;
    float t = tempco->temperature;

    if (t < VDDC_VDDF_TEMPCO_THRESHOLD && t >= LOW_LIMIT)
        range = TEMPCO_RANGE_LOW;
    else if (t >= VDDC_VDDF_TEMPCO_THRESHOLD && t < BUCK_LP_TEMP_THRESHOLD)
        range = TEMPCO_RANGE_MID;
    else if (t >= BUCK_LP_TEMP_THRESHOLD && t < HIGH_LIMIT)
        range = TEMPCO_RANGE_HIGH;
    else
        range = TEMPCO_OUT_OF_RANGE;

    switch (range) {
    case TEMPCO_RANGE_LOW:
        if (g2_spotmgr_is_pcm2p0 == 0u)
            g2_spotmgr_frc_buck_act = 0u;
        spotmgr_pcm2_0_vddc_vddf_tempco_top_5a00c8(TEMPCO_RANGE_LOW);
        tempco->range_lower = LOW_LIMIT;
        tempco->range_higher = VDDC_VDDF_TEMPCO_THRESHOLD;
        break;
    case TEMPCO_RANGE_MID:
        if (g2_spotmgr_is_pcm2p0 == 0u)
            g2_spotmgr_frc_buck_act = 0u;
        spotmgr_pcm2_0_vddc_vddf_tempco_top_5a00c8(TEMPCO_RANGE_MID);
        tempco->range_lower = VDDC_VDDF_TEMPCO_THRESHOLD - TEMP_HYSTERESIS;
        tempco->range_higher = BUCK_LP_TEMP_THRESHOLD;
        break;
    case TEMPCO_RANGE_HIGH:
        if (g2_spotmgr_is_pcm2p0 == 0u)
            g2_spotmgr_frc_buck_act = 1u;
        spotmgr_pcm2_0_vddc_vddf_tempco_top_5a00c8(TEMPCO_RANGE_HIGH);
        tempco->range_lower = BUCK_LP_TEMP_THRESHOLD - TEMP_HYSTERESIS;
        tempco->range_higher = HIGH_LIMIT;
        break;
    default:
        tempco->range_lower = 0.0f;
        tempco->range_higher = 0.0f;
        return 1u;
    }
    return 0u;
}

/* PCM2.0 only: keep the buck active in deep sleep for the HIGH temperature range
 * or when STIMER / any enabled TIMER runs from HFRC, HFRC2 or a GPIO clock. */
void spotmgr_pcm2_0_buck_deepsleep_state_determine_5a0204(void)
{
    if (g2_spotmgr_is_pcm2p0 == 0u)
        return;
    if (g2_spotmgr_pcm2_0_tempco_range == TEMPCO_RANGE_HIGH) {
        g2_spotmgr_frc_buck_act = 1u;
        return;
    }
    if (am_hal_stimer_is_running_48d620() && (STIMER_STCFG & 0xfu) >= 1u &&
        (STIMER_STCFG & 0xfu) <= 2u) {
        g2_spotmgr_frc_buck_act = 1u;
        return;
    }
    for (uint32_t n = 0u; n < 16u; n++) {
        if ((TIMER_CTRL0(n) & 1u) == 0u || ((TIMER_GLOBEN >> n) & 1u) == 0u)
            continue;
        uint32_t clk = (TIMER_CTRL0(n) & 0x1ffffu) >> 8;
        if (clk < 6u || (clk >= 19u && clk <= 24u) || (clk >= 256u && clk <= 479u)) {
            g2_spotmgr_frc_buck_act = 1u;
            return;
        }
    }
    g2_spotmgr_frc_buck_act = 0u;
}

uint32_t spotmgr_pcm2_0_gpu_on_sequence_5a0328(uint8_t state)
{
    if (SIMOBUCK_ACTIVE()) {
        if (g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 != 0u) {
            g2_spotmgr_pcm2_0_cur_coreldotempcotrim_buck = (MCUCTRL_LDOREG1 & 0x3fffu) >> 10;
            FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, 1u);
        }
        uint32_t core = MCUCTRL_LDOREG1 & 0x3ffu;
        uint32_t core_diff = core + CORELDOTRIM_BOOST_CODE_FOR_GPU < 0x400u ?
                             CORELDOTRIM_BOOST_CODE_FOR_GPU : 0x3ffu - core;
        FIELD_SET(MCUCTRL_LDOREG1, 0x3ffu, 0, core_diff + MCUCTRL_LDOREG1);
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, 5u);
        audio_delay_us(5u);
        if (g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 != 0u) {
            uint32_t vddf = (MCUCTRL_VREFGEN4 & 0x7fu) + TVRGFVREFTRIM_BOOST_CODE_FOR_GPU;
            FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0, vddf < 0x80u ? vddf : 0x7fu);
        }
        MCUCTRL_PWRSW1 |= 0x20000000u;
        MCUCTRL_PWRSW1 |= 0x10000000u;
        MCUCTRL_PWRSW1 |= 0x80000000u;
        MCUCTRL_PWRSW1 |= 0x40000000u;
        audio_delay_us(10u);
        if (g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 != 0u) {
            uint32_t vddc = (MCUCTRL_VREFGEN2 & 0x7fu) + TVRGCVREFTRIM_BOOST_CODE_FOR_GPU;
            FIELD_SET(MCUCTRL_VREFGEN2, 0x7fu, 0, vddc < 0x80u ? vddc : 0x7fu);
            MCUCTRL_D2ASPARE |= 0x100u;
        }
        if (g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 == 0u) {
            FIELD_SET(MCUCTRL_SIMOBUCK2, 0x3e000000u, 25, 6u);
            FIELD_SET(MCUCTRL_SIMOBUCK2, 0xf800u, 11, 6u);
            FIELD_SET(MCUCTRL_SIMOBUCK4, 0x3e000000u, 25, 5u);
            FIELD_SET(MCUCTRL_SIMOBUCK4, 0xf800u, 11, 5u);
            if (state == GPUSTATE_ACTIVE_LP) {
                FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8, 9u);
                FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17, 13u);
            } else {
                FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8, 13u);
                FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17, 19u);
            }
        } else {
            FIELD_SET(MCUCTRL_SIMOBUCK2, 0x3e000000u, 25, 10u);
            FIELD_SET(MCUCTRL_SIMOBUCK2, 0xf800u, 11, 10u);
            FIELD_SET(MCUCTRL_SIMOBUCK4, 0x3e000000u, 25, 8u);
            FIELD_SET(MCUCTRL_SIMOBUCK4, 0xf800u, 11, 8u);
            if (state == GPUSTATE_ACTIVE_LP) {
                FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8, 16u);
                FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17, 20u);
            } else {
                FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8, 20u);
                FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17, 22u);
            }
        }
        MCUCTRL_PWRSW1 &= ~0x20000000u;
        MCUCTRL_PWRSW1 &= ~0x10000000u;
        MCUCTRL_PWRSW1 &= ~0x80000000u;
        MCUCTRL_PWRSW1 &= ~0x40000000u;
        uint32_t ldoreg1 = MCUCTRL_LDOREG1;
        MCUCTRL_LDOREG1 = ((ldoreg1 - core_diff) & 0x3ffu) | (ldoreg1 & ~0x3ffu);
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, g2_spotmgr_pcm2_0_is_b0_pcm1p0 != 0u ? 0u : 1u);
    } else {
        g2_spotmgr_pcm2_0_cur_coreldotempcotrim_ldo = (MCUCTRL_LDOREG1 & 0x3fffu) >> 10;
        FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, 2u);
        g2_spotmgr_pcm2_0_cur_memldoactivetrim_ldo = MCUCTRL_LDOREG2 & 0x3fu;
        uint32_t mem = (MCUCTRL_LDOREG2 & 0x3fu) + 5u;
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, mem < 0x40u ? mem : 0x3fu);
        audio_delay_us(15u);
    }
    return 0u;
}

uint32_t spotmgr_pcm2_0_gpu_off_sequence_5a05e0(void)
{
    if (SIMOBUCK_ACTIVE()) {
        uint32_t core = MCUCTRL_LDOREG1 & 0x3ffu;
        uint32_t core_diff = core + CORELDOTRIM_BOOST_CODE_FOR_GPU < 0x400u ?
                             CORELDOTRIM_BOOST_CODE_FOR_GPU : 0x3ffu - core;
        FIELD_SET(MCUCTRL_LDOREG1, 0x3ffu, 0, core_diff + MCUCTRL_LDOREG1);
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, 5u);
        audio_delay_us(5u);
        MCUCTRL_PWRSW1 |= 0x20000000u;
        MCUCTRL_PWRSW1 |= 0x10000000u;
        MCUCTRL_PWRSW1 |= 0x80000000u;
        MCUCTRL_PWRSW1 |= 0x40000000u;
        audio_delay_us(10u);
        FIELD_SET(MCUCTRL_SIMOBUCK2, 0x3e000000u, 25, 6u);
        FIELD_SET(MCUCTRL_SIMOBUCK2, 0xf800u, 11, 6u);
        FIELD_SET(MCUCTRL_SIMOBUCK4, 0x3e000000u, 25, 5u);
        FIELD_SET(MCUCTRL_SIMOBUCK4, 0xf800u, 11, 5u);
        FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8, 7u);
        FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17, 10u);
        if (g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 != 0u) {
            uint32_t vddf = MCUCTRL_VREFGEN4 & 0x7fu;
            FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0,
                      vddf > TVRGFVREFTRIM_BOOST_CODE_FOR_GPU ? vddf - TVRGFVREFTRIM_BOOST_CODE_FOR_GPU : 0u);
            uint32_t vddc = MCUCTRL_VREFGEN2 & 0x7fu;
            FIELD_SET(MCUCTRL_VREFGEN2, 0x7fu, 0,
                      vddc > TVRGCVREFTRIM_BOOST_CODE_FOR_GPU ? vddc - TVRGCVREFTRIM_BOOST_CODE_FOR_GPU : 0u);
            FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, g2_spotmgr_pcm2_0_cur_coreldotempcotrim_buck);
            MCUCTRL_D2ASPARE &= ~0x100u;
        }
        uint32_t ldoreg1 = MCUCTRL_LDOREG1;
        MCUCTRL_LDOREG1 = ((ldoreg1 - core_diff) & 0x3ffu) | (ldoreg1 & ~0x3ffu);
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, g2_spotmgr_pcm2_0_is_b0_pcm1p0 != 0u ? 0u : 1u);
        MCUCTRL_PWRSW1 &= ~0x20000000u;
        MCUCTRL_PWRSW1 &= ~0x10000000u;
        MCUCTRL_PWRSW1 &= ~0x80000000u;
        MCUCTRL_PWRSW1 &= ~0x40000000u;
    } else {
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, g2_spotmgr_pcm2_0_cur_memldoactivetrim_ldo);
        FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, g2_spotmgr_pcm2_0_cur_coreldotempcotrim_ldo);
    }
    return 0u;
}

uint32_t spotmgr_pcm2_0_power_state_update_5a0786(uint8_t stimulus, bool on, void *args)
{
    (void)on;
    switch (stimulus) {
    case STIM_CPU_STATE:
        if (args != NULL && *(const uint8_t *)args == CPUSTATE_SLEEP_DEEP)
            spotmgr_pcm2_0_buck_deepsleep_state_determine_5a0204();
        return 0u;
    case STIM_GPU_STATE: {
        uint8_t state = *(const uint8_t *)args;
        if (state == GPUSTATE_OFF)
            return spotmgr_pcm2_0_gpu_off_sequence_5a05e0();
        return spotmgr_pcm2_0_gpu_on_sequence_5a0328(state);
    }
    case STIM_TEMP:
        return spotmgr_pcm2_0_tempco_update_5a00fc(args);
    default:
        return 0u;
    }
}

/* B2 PCM2.0 parts are SDIO-screened when FT1_GDR1 dates them 2024-12-20 or later
 * (FT1REV 0); B1 PCM2.0 parts are always unscreened. */
uint32_t spotmgr_pcm2_0_init_5a08e4(void)
{
    uint32_t rev = MCUCTRL_CHIPREV & 0xffu;
    uint32_t trim = g2_pwrctrl_trim_version;

    g2_spotmgr_pcm2_0_is_b0_pcm1p0 = (rev == 0x21u && trim == 2u) ? 1u : 0u;
    g2_spotmgr_pcm2_0_is_pcm1p0_or_1p1 =
        ((rev == 0x21u && trim == 2u) || (rev == 0x21u && trim == 3u) ||
         (rev == 0x22u && trim == 0u)) ? 1u : 0u;

    if (rev == 0x22u && trim == 1u) {
        g2_spotmgr_pcm2_0_is_pcm2p0_unscreened = 1u;
    } else if (rev == 0x23u && trim == 0u) {
        uint32_t gdr1 = *(volatile const uint32_t *)(volatile const void *)(g2_pwrctrl_info1_regs + 0x44);
        bool screened = ((gdr1 & 0x3fe00000u) == 0x31800000u &&            /* 2024-12 */
                         ((gdr1 & 0x1fffffu) >> 16) >= 20u && (gdr1 & 0xffffu) == 0u) ||
                        (((gdr1 & 0x3fffffffu) >> 25) >= 25u && (gdr1 & 0xffffu) == 0u);
        g2_spotmgr_pcm2_0_is_pcm2p0_unscreened = screened ? 0u : 1u;
    } else {
        g2_spotmgr_pcm2_0_is_pcm2p0_unscreened = 0u;
    }
    return 0u;
}
