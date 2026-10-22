/* AmbiqSuite Apollo510 HAL, mcu/apollo510/hal/am_hal_spotmgr_pcm0_7.c (BSD-3-Clause, Ambiq Micro).
 * Stock-variant reconstruction of the PCM0.7 (B0, trim 1) SPOT-manager family,
 * native 0x59fb70..0x5a001c (0x59fd82..0x59fe58 = simobuck_init_bfr/aft_enable and
 * ton_config_init belong to other units).
 *
 * The bodies match the pinned SDK 5.1.0 text (ambiqhal_ambiq 5efc0228). The
 * static inline simobuck_enable and the two GPU sequences are separate functions
 * in stock, power_state_update has no STIM_INIT_STATE case of its own (all
 * stimuli other than GPU and TEMP fall through to success), and the temperature
 * bounds are stored as their IEEE bit patterns so the unit stays integer-only.
 * Installed by am_hal_spotmgr_init 0x480434 (hal/p-06-spotmgr) for CHIPREV 0x21
 * with trim version 1. */
#include <stdint.h>
#include <stdbool.h>

#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define MCUCTRL_VREFGEN2   REG(0x40020044u) /* TVRGCVREFTRIM [6:0] */
#define MCUCTRL_VREFGEN4   REG(0x4002004cu) /* TVRGFVREFTRIM [6:0] */
#define MCUCTRL_LDOREG1    REG(0x40020080u) /* CORELDOACTIVETRIM [9:0], CORELDOTEMPCOTRIM [13:10] */
#define MCUCTRL_LDOREG2    REG(0x40020088u) /* MEMLDOACTIVETRIM [5:0] */
#define MCUCTRL_D2ASPARE   REG(0x400201b0u) /* SIMOVDDCBOOST [8] */
#define MCUCTRL_SIMOBUCK1  REG(0x40020340u) /* SIMOBUCKHPTRIMEN [31] */
#define MCUCTRL_SIMOBUCK2  REG(0x40020344u) /* VDDCACTLOWTONTRIM [29:25], VDDCACTHIGHTONTRIM [15:11] */
#define MCUCTRL_SIMOBUCK4  REG(0x4002034cu) /* VDDCLVACTLOWTONTRIM [29:25], VDDCLVACTHIGHTONTRIM [15:11] */
#define MCUCTRL_SIMOBUCK6  REG(0x40020354u) /* VDDFACTHIGHTONTRIM [21:17] */
#define MCUCTRL_SIMOBUCK7  REG(0x40020358u) /* VDDFACTLOWTONTRIM [12:8] */
#define MCUCTRL_SIMOBUCK14 REG(0x40020374u) /* VDDCLKGTRIM [30:29] */
#define PWRCTRL_VRCTRL     REG(0x40021100u) /* SIMOBUCKEN [0] */
#define PWRCTRL_VRSTATUS   REG(0x40021108u) /* SIMOBUCKST [5:4], 3 = active */

#define FIELD_SET(reg, mask, shift, v) ((reg) = ((reg) & ~(uint32_t)(mask)) | (((uint32_t)(v) << (shift)) & (mask)))
#define SIMOBUCK_ACTIVE() (((PWRCTRL_VRSTATUS & 0x3fu) >> 4) == 3u)

/* am_hal_spotmgr_gpu_state_e / am_hal_spotmgr_stimulus_e values seen in stock. */
enum { GPUSTATE_OFF = 0, GPUSTATE_ACTIVE_LP = 1, GPUSTATE_ACTIVE_HP = 2 };
enum { STIM_CPU_STATE = 0, STIM_GPU_STATE = 1, STIM_TEMP = 2 };

/* am_hal_spotmgr_tempco_param_t with the floats kept as bit patterns. */
typedef struct {
    uint32_t temperature; /* +0x0 float */
    uint32_t range_lower; /* +0x4 float */
    uint32_t range_higher; /* +0x8 float */
} g2_spotmgr_tempco_bits_t;

#define LOW_LIMIT_BITS  0xc3888000u /* -273.0f */
#define HIGH_LIMIT_BITS 0x447a0000u /* 1000.0f */

extern volatile uint8_t g2_spotmgr_orig_trims_stored;       /* RAM 0x20074f63, g_bOrigTrimsStored */
extern volatile uint32_t g2_spotmgr_orig_tvrgcvreftrim;     /* RAM 0x2007426c, g_orig_TVRGCVREFTRIM */
extern volatile uint32_t g2_spotmgr_orig_tvrgfvreftrim;     /* RAM 0x20074270, g_orig_TVRGFVREFTRIM */
extern volatile uint32_t g2_spotmgr_orig_vddclkgtrim;       /* RAM 0x20074274, g_orig_VDDCLKGTRIM */
extern volatile uint32_t g2_spotmgr_orig_coreldotempcotrim; /* RAM 0x20074278, g_orig_CORELDOTEMPCOTRIM */
extern volatile uint32_t g2_spotmgr_pcm0_7_cur_coreldotempcotrim_ldo; /* RAM 0x200742b4 */
extern volatile uint32_t g2_spotmgr_pcm0_7_cur_memldoactivetrim_ldo;  /* RAM 0x200742b8 */
extern volatile uint8_t g2_spotmgr_vddc_act_low_ton_trim;    /* RAM 0x2000453a */
extern volatile uint8_t g2_spotmgr_vddc_act_high_ton_trim;   /* RAM 0x2000453b */
extern volatile uint8_t g2_spotmgr_vddclv_act_low_ton_trim;  /* RAM 0x2000453c */
extern volatile uint8_t g2_spotmgr_vddclv_act_high_ton_trim; /* RAM 0x2000453d */
extern volatile uint8_t g2_spotmgr_vddf_act_low_ton_trim;    /* RAM 0x2000453e */
extern volatile uint8_t g2_spotmgr_vddf_act_high_ton_trim;   /* RAM 0x2000453f */
/* ui8TonActiveConfig[GPU TON state][CPU TON state], 1 = SYSCTRL_TON_LEVEL_LOW. */
extern const uint8_t g2_spotmgr_ton_active_config[3][3];     /* ROM 0x789fe0 */

extern void buck_ldo_update_override_47fe6c(bool enable);
extern void audio_delay_us(uint32_t);                          /* am_hal_delay_us 0x4807a0 */
extern uint32_t am_hal_spotmgr_ton_config_update_4803c2(bool gpu_on, uint32_t gpu_mode);

/* simobuck_enable (inline in the SDK). */
void spotmgr_pcm0_7_simobuck_enable_59fb70(bool enable)
{
    if (enable) {
        PWRCTRL_VRCTRL |= 1u;
        audio_delay_us(5u);
        buck_ldo_update_override_47fe6c(true);
    } else {
        buck_ldo_update_override_47fe6c(false);
        audio_delay_us(5u);
        PWRCTRL_VRCTRL &= ~1u;
    }
}

uint32_t spotmgr_pcm0_7_gpu_on_sequence_59fbac(uint8_t state)
{
    if (state != GPUSTATE_ACTIVE_HP)
        (void)am_hal_spotmgr_ton_config_update_4803c2(true, 0u /* GPU_MODE_LOW_POWER */);

    if (SIMOBUCK_ACTIVE()) {
        if (g2_spotmgr_orig_trims_stored != 0u) {
            spotmgr_pcm0_7_simobuck_enable_59fb70(false);
            FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, 1u);
            uint32_t vddc = g2_spotmgr_orig_tvrgcvreftrim + 9u;
            FIELD_SET(MCUCTRL_VREFGEN2, 0x7fu, 0, vddc < 0x80u ? vddc : 0x7fu);
            MCUCTRL_D2ASPARE |= 0x100u;
            uint32_t vddf = g2_spotmgr_orig_tvrgfvreftrim + 15u;
            FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0, vddf < 0x80u ? vddf : 0x7fu);
            MCUCTRL_SIMOBUCK14 |= 0x60000000u; /* VDDCLKGTRIM = 3 */
            spotmgr_pcm0_7_simobuck_enable_59fb70(true);
            audio_delay_us(15u);
        }
    } else {
        g2_spotmgr_pcm0_7_cur_coreldotempcotrim_ldo = (MCUCTRL_LDOREG1 & 0x3fffu) >> 10;
        FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, 2u);
        g2_spotmgr_pcm0_7_cur_memldoactivetrim_ldo = MCUCTRL_LDOREG2 & 0x3fu;
        uint32_t mem = (MCUCTRL_LDOREG2 & 0x3fu) + 5u;
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, mem < 0x40u ? mem : 0x3fu);
        audio_delay_us(15u);
    }
    return 0u;
}

uint32_t spotmgr_pcm0_7_gpu_off_sequence_59fca2(void)
{
    if (SIMOBUCK_ACTIVE()) {
        if (g2_spotmgr_orig_trims_stored != 0u) {
            spotmgr_pcm0_7_simobuck_enable_59fb70(false);
            FIELD_SET(MCUCTRL_SIMOBUCK14, 0x60000000u, 29, g2_spotmgr_orig_vddclkgtrim);
            FIELD_SET(MCUCTRL_VREFGEN4, 0x7fu, 0, g2_spotmgr_orig_tvrgfvreftrim);
            MCUCTRL_D2ASPARE &= ~0x100u;
            FIELD_SET(MCUCTRL_VREFGEN2, 0x7fu, 0, g2_spotmgr_orig_tvrgcvreftrim);
            FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, g2_spotmgr_orig_coreldotempcotrim);
            spotmgr_pcm0_7_simobuck_enable_59fb70(true);
        }
    } else {
        FIELD_SET(MCUCTRL_LDOREG2, 0x3fu, 0, g2_spotmgr_pcm0_7_cur_memldoactivetrim_ldo);
        FIELD_SET(MCUCTRL_LDOREG1, 0x3c00u, 10, g2_spotmgr_pcm0_7_cur_coreldotempcotrim_ldo);
    }
    (void)am_hal_spotmgr_ton_config_update_4803c2(false, 0u);
    return 0u;
}

/* GPU state drives the on/off sequences; TEMP reports the full range; every
 * other stimulus is a no-op returning success. */
uint32_t spotmgr_pcm0_7_power_state_update_59fd36(uint8_t stimulus, bool on, void *args)
{
    (void)on;
    switch (stimulus) {
    case STIM_GPU_STATE: {
        uint8_t state = *(const uint8_t *)args;
        if (state == GPUSTATE_OFF)
            (void)spotmgr_pcm0_7_gpu_off_sequence_59fca2();
        else
            (void)spotmgr_pcm0_7_gpu_on_sequence_59fbac(state);
        break;
    }
    case STIM_TEMP: {
        g2_spotmgr_tempco_bits_t *tempco = args;
        tempco->range_lower = LOW_LIMIT_BITS;
        tempco->range_higher = HIGH_LIMIT_BITS;
        break;
    }
    default:
        break;
    }
    return 0u;
}

uint32_t spotmgr_pcm0_7_ton_config_update_59fe5a(bool gpu_on, uint8_t gpu_mode)
{
    uint32_t simobuck_on = PWRCTRL_VRCTRL;
    if ((simobuck_on & 1u) != 0u) {
        buck_ldo_update_override_47fe6c(false);
        audio_delay_us(5u);
        PWRCTRL_VRCTRL &= ~1u;
    }

    uint32_t gpu_ton = 0u; /* SYSCTRL_GPU_TON_POWER_STATE_OFF */
    if (gpu_on)
        gpu_ton = (gpu_mode == 0u) ? 1u : 2u; /* LP : HP */
    bool lp_low = g2_spotmgr_ton_active_config[gpu_ton][1] == 1u;
    bool hp_low = g2_spotmgr_ton_active_config[gpu_ton][2] == 1u;

    MCUCTRL_SIMOBUCK1 |= 0x80000000u;
    FIELD_SET(MCUCTRL_SIMOBUCK2, 0x3e000000u, 25,
              lp_low ? g2_spotmgr_vddc_act_low_ton_trim : g2_spotmgr_vddc_act_high_ton_trim);
    FIELD_SET(MCUCTRL_SIMOBUCK2, 0xf800u, 11,
              hp_low ? g2_spotmgr_vddc_act_low_ton_trim : g2_spotmgr_vddc_act_high_ton_trim);
    FIELD_SET(MCUCTRL_SIMOBUCK7, 0x1f00u, 8,
              lp_low ? g2_spotmgr_vddf_act_low_ton_trim : g2_spotmgr_vddf_act_high_ton_trim);
    FIELD_SET(MCUCTRL_SIMOBUCK6, 0x3e0000u, 17,
              hp_low ? g2_spotmgr_vddf_act_low_ton_trim : g2_spotmgr_vddf_act_high_ton_trim);
    FIELD_SET(MCUCTRL_SIMOBUCK4, 0x3e000000u, 25,
              lp_low ? g2_spotmgr_vddclv_act_low_ton_trim : g2_spotmgr_vddclv_act_high_ton_trim);
    FIELD_SET(MCUCTRL_SIMOBUCK4, 0xf800u, 11,
              hp_low ? g2_spotmgr_vddclv_act_low_ton_trim : g2_spotmgr_vddclv_act_high_ton_trim);

    if ((simobuck_on & 1u) != 0u) {
        PWRCTRL_VRCTRL |= 1u;
        audio_delay_us(5u);
        buck_ldo_update_override_47fe6c(true);
    }
    return 0u;
}

uint32_t spotmgr_pcm0_7_init_5a0018(void)
{
    return 0u;
}
