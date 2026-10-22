/* AmbiqSuite Apollo510 HAL mcu_hp_lp_switch_sequence / am_hal_pwrctrl_mcu_mode_select
 * (mcu/apollo510/hal/am_hal_pwrctrl.c, BSD-3-Clause), stock variant.
 * Native 0x47ef74..0x47f09f (switch sequence) and 0x47f0a0..0x47f107
 * (mode select); literal pools 0x47f94c.., 0x47fab4..0x47fabf.
 *
 * am_hal_pwrctrl_mcu_mode_select matches the pinned public 5.1.0 replay
 * (third-party/upstream/ambiqhal-apollo510). The switch sequence is an older
 * revision: it ignores the am_hal_spotmgr_power_state_update return values
 * (5.1.0 only switches when the HP report succeeds and returns the LP report
 * status), always runs am_hal_spotmgr_post_lptohp_handle after the HP path,
 * and returns AM_HAL_STATUS_FAIL (1) when HFRC2 never becomes ready. Called
 * with HIGH_PERFORMANCE from the board init sequence 0x5cdd14. */
#include <stdint.h>

#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))

#define CLKGEN_CLOCKENSTAT 0x40004030u /* HFRC2READY bit 24 */
#define CLKGEN_MISC        0x40004044u /* FRCHFRC2 bit 5 */
#define PWRCTRL_MCUPERFREQ 0x40021000u /* MCUPERFREQ [1:0], MCUPERFACK bit 2, MCUPERFSTATUS [4:3] */
#define PWRCTRL_VRSTATUS   0x40021108u /* SIMOBUCKST [5:4] */

#define MCU_MODE_LOW_POWER        1u
#define MCU_MODE_HIGH_PERFORMANCE 2u
#define SIMOBUCKST_ACT            3u
#define STIM_CPU_STATE            0u
#define CPUSTATE_ACTIVE_LP        0u
#define CPUSTATE_ACTIVE_HP        1u
#define PERF_SWITCH_WAIT_US       20u /* AM_HAL_PWRCTRL_PERF_SWITCH_WAIT_US */
#define HFRC2_DELAY_US            15u /* AM_HAL_CLKGEN_HFRC2_DELAY */

#define STATUS_SUCCESS           0u
#define STATUS_FAIL              1u
#define STATUS_TIMEOUT           4u
#define STATUS_INVALID_ARG       6u
#define STATUS_INVALID_OPERATION 7u

extern uint8_t g2_pwrctrl_cur_mcu_mode_20004538; /* RAM 0x20004538 g_eCurMcuPwrMode */

extern uint32_t g2_main_critical_save_473940(void);               /* am_hal_interrupt_master_disable */
extern uint32_t audio_ble_flash_control(uint32_t stimulus, uint32_t update,
                                        const uint32_t *args);  /* 0x480312 am_hal_spotmgr_power_state_update */
extern uint32_t am_hal_spotmgr_post_lptohp_handle_4803dc(void);
extern void audio_delay_us(uint32_t us);                          /* 0x4807a0 am_hal_delay_us */
extern uint32_t audio_wait4(uint32_t budget, uint32_t address, uint32_t mask,
                            uint32_t expected);                   /* 0x4807fc am_hal_delay_us_status_change */

uint32_t mcu_hp_lp_switch_sequence_47ef74(uint32_t mode);
uint32_t am_hal_pwrctrl_mcu_mode_select_47f0a0(uint32_t mode);

static void report_cpu_state(const uint8_t *state)
{
    (void)audio_ble_flash_control(STIM_CPU_STATE, 0u, (const uint32_t *)(const void *)state);
}

static uint32_t set_mode_and_wait(uint32_t mode)
{
    uint32_t status;
    uint32_t i;

    REG(PWRCTRL_MCUPERFREQ) = (REG(PWRCTRL_MCUPERFREQ) & ~3u) | (mode & 3u);
    status = STATUS_TIMEOUT;
    for (i = 0u; i < PERF_SWITCH_WAIT_US; i++) {
        if (((REG(PWRCTRL_MCUPERFREQ) >> 2) & 1u) >= 1u) {
            status = STATUS_SUCCESS;
            break;
        }
        audio_delay_us(1u);
    }
    return status;
}

uint32_t mcu_hp_lp_switch_sequence_47ef74(uint32_t mode)
{
    uint8_t lp_after_switch;
    uint8_t lp_revert;
    uint32_t status;
    uint32_t const primask = g2_main_critical_save_473940();

    mode = (uint8_t)mode;
    if (mode == MCU_MODE_HIGH_PERFORMANCE) {
        uint8_t const hp = CPUSTATE_ACTIVE_HP;
        uint8_t hfrc2_forced = 0u;

        report_cpu_state(&hp);
        if (((REG(CLKGEN_MISC) >> 5) & 1u) == 0u) {
            REG(CLKGEN_MISC) |= 0x20u;
            audio_delay_us(1u);
            (void)audio_wait4(HFRC2_DELAY_US, CLKGEN_CLOCKENSTAT, 1u << 24, 1u << 24);
            hfrc2_forced = 1u;
        }
        if (((REG(CLKGEN_CLOCKENSTAT) >> 24) & 1u) == 0u)
            status = STATUS_FAIL;
        else
            status = set_mode_and_wait(mode);
        if (hfrc2_forced != 0u)
            REG(CLKGEN_MISC) &= ~0x20u;
        (void)am_hal_spotmgr_post_lptohp_handle_4803dc();
    } else {
        status = set_mode_and_wait(mode);
    }

    if (status == STATUS_SUCCESS) {
        g2_pwrctrl_cur_mcu_mode_20004538 = (uint8_t)mode;
        if (mode != MCU_MODE_HIGH_PERFORMANCE) {
            lp_after_switch = CPUSTATE_ACTIVE_LP;
            report_cpu_state(&lp_after_switch);
        }
    } else if (mode == MCU_MODE_HIGH_PERFORMANCE) {
        lp_revert = CPUSTATE_ACTIVE_LP;
        report_cpu_state(&lp_revert);
    }

    __asm__ volatile("msr primask, %0" : : "r"(primask) : "memory");
    return status;
}

uint32_t am_hal_pwrctrl_mcu_mode_select_47f0a0(uint32_t mode)
{
    uint32_t status;

    mode = (uint8_t)mode;
    if (mode != MCU_MODE_LOW_POWER && mode != MCU_MODE_HIGH_PERFORMANCE)
        return STATUS_INVALID_ARG;
    if (mode == MCU_MODE_HIGH_PERFORMANCE && ((REG(PWRCTRL_VRSTATUS) >> 4) & 3u) != SIMOBUCKST_ACT)
        return STATUS_INVALID_OPERATION;
    if (mode == g2_pwrctrl_cur_mcu_mode_20004538)
        return STATUS_SUCCESS;
    status = mcu_hp_lp_switch_sequence_47ef74(mode);
    if (status != STATUS_SUCCESS)
        return status;
    return ((REG(PWRCTRL_MCUPERFREQ) >> 3) & 3u) == mode ? STATUS_SUCCESS : STATUS_FAIL;
}
