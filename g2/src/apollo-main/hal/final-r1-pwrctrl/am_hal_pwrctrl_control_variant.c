/* AmbiqSuite Apollo510 HAL am_hal_pwrctrl_control
 * (mcu/apollo510/hal/am_hal_pwrctrl.c, BSD-3-Clause, Ambiq Micro), stock variant.
 * Native 0x47fea0..0x47ffba; literal pools 0x48010c..0x480110, 0x480188, 0x4801d4..0x4801ec.
 *
 * Same revision as the other am_hal_pwrctrl.c variants in g2/src
 * (hal/x-03-pwrctrl, runtime/info-memory/memory.c): the SIMOBUCK_INIT,
 * CRYPTO_POWERDOWN and XTAL_PWDN_DEEPSLEEP cases match the pinned public
 * 5.1.0 replay, but DIS_PERIPHS_ALL ignores both
 * am_hal_spotmgr_power_state_update results (5.1.0 returns them) and returns
 * the status of the second register wait, i.e. 0 on success. */
#include <stdint.h>

#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))

#define PWRCTRL_DEVPWREN     0x40021004u
#define PWRCTRL_AUDSSPWREN   0x4002100cu
#define PWRCTRL_VRCTRL       0x40021100u /* SIMOBUCKEN bit 0 */
#define PWRCTRL_VRSTATUS     0x40021108u /* SIMOBUCKST [5:4] */
#define MCUCTRL_XTALCTRL     0x40020120u
#define MCUCTRL_XTALGENCTRL  0x40020124u /* XTALBIASTRIM [7:2] */
#define MCUCTRL_DBGCTRL      0x40020250u /* DBGTPIUTRACEENABLE bit 0, DBGTPIUCLKSEL [3:1] */
#define MCUCTRL_SIMOBUCK0    0x4002033cu /* VDDC/VDDF/VDDS/VDDCLV RXCOMPEN [3:0] */
#define MCUCTRL_SIMOBUCK15   0x40020378u /* TRIMLATCHOVER bit 31 */
#define DCB_DEMCR            0xe000edfcu /* TRCENA bit 24 */

#define CONTROL_SIMOBUCK_INIT       0u
#define CONTROL_CRYPTO_POWERDOWN    1u
#define CONTROL_XTAL_PWDN_DEEPSLEEP 2u
#define CONTROL_DIS_PERIPHS_ALL     3u

#define PERIPH_CRYPTO          0x17u
#define SIMOBUCKST_ACT         3u
#define MAX_WAIT_US            5u
#define DEVPWRST_ALL_MASK      0x3fffffffu
#define AUDSSPWRST_ALL_MASK    0x4c4u
#define STIM_DEVPWR            3u
#define STIM_AUDSSPWR          4u
#define STATUS_SUCCESS         0u
#define STATUS_INVALID_ARG     6u

/* am_hal_delay_us_status_check(max_us, address, mask, value, wait_for_equal) */
extern uint32_t g2_main_mspi_status_poll_480826(uint32_t count, uintptr_t address,
                                                uint32_t mask, uint32_t expected,
                                                uint32_t equal);
/* am_hal_spotmgr_power_state_update(stimulus, on, args) */
extern uint32_t audio_ble_flash_control(uint32_t stimulus, uint32_t update,
                                        const uint32_t *args); /* 0x480312 */
/* am_hal_pwrctrl_periph_enabled(peripheral, &enabled) */
extern uint32_t audio_uart_nema_power_status_47f90c(uint32_t peripheral, uint8_t *powered);
/* am_hal_pwrctrl_periph_disable(peripheral) */
extern uint32_t audio_power_peripheral_off(uint32_t peripheral); /* 0x47f7ae */
extern uint32_t crypto_quiesce_47f56e(void);
extern void buck_ldo_override_init_47fe12(void);
extern uint32_t am_hal_spotmgr_simobuck_init_bfr_ovr_480358(void);
extern uint32_t am_hal_spotmgr_simobuck_init_bfr_enable_48036e(void);
extern uint32_t am_hal_spotmgr_simobuck_init_aft_enable_480384(void);

uint32_t am_hal_pwrctrl_control_47fea0(uint32_t control, void *args);

uint32_t am_hal_pwrctrl_control_47fea0(uint32_t control, void *args)
{
    uint32_t status = STATUS_SUCCESS;
    uint32_t all_disabled;
    uint8_t enabled;

    (void)args;
    switch ((uint8_t)control) {
    case CONTROL_SIMOBUCK_INIT:
        if (((REG(PWRCTRL_VRSTATUS) >> 4) & 3u) == SIMOBUCKST_ACT)
            return STATUS_SUCCESS;
        (void)am_hal_spotmgr_simobuck_init_bfr_ovr_480358();
        buck_ldo_override_init_47fe12();
        REG(MCUCTRL_SIMOBUCK15) |= 0x80000000u;
        REG(MCUCTRL_SIMOBUCK0) |= 0xfu;
        (void)am_hal_spotmgr_simobuck_init_bfr_enable_48036e();
        REG(PWRCTRL_VRCTRL) |= 1u;
        (void)am_hal_spotmgr_simobuck_init_aft_enable_480384();
        break;

    case CONTROL_CRYPTO_POWERDOWN:
        enabled = 0u;
        (void)audio_uart_nema_power_status_47f90c(PERIPH_CRYPTO, &enabled);
        if (enabled != 0u) {
            status = crypto_quiesce_47f56e();
            if (status != STATUS_SUCCESS)
                return status;
            status = audio_power_peripheral_off(PERIPH_CRYPTO);
            if (status != STATUS_SUCCESS)
                return status;
        }
        break;

    case CONTROL_XTAL_PWDN_DEEPSLEEP:
        REG(MCUCTRL_XTALGENCTRL) = (REG(MCUCTRL_XTALGENCTRL) & ~0xfcu) | (0x20u << 2);
        REG(MCUCTRL_XTALCTRL) = 1u; /* XTALSWE override, core/comp powered down */
        break;

    case CONTROL_DIS_PERIPHS_ALL:
        REG(DCB_DEMCR) &= ~0x01000000u;
        REG(MCUCTRL_DBGCTRL) &= ~1u;
        REG(MCUCTRL_DBGCTRL) &= ~0xeu;
        REG(PWRCTRL_DEVPWREN) = 0u;
        REG(PWRCTRL_AUDSSPWREN) = 0u;
        status = g2_main_mspi_status_poll_480826(MAX_WAIT_US, PWRCTRL_DEVPWREN,
                                                 DEVPWRST_ALL_MASK, 0u, 1u);
        if (status != STATUS_SUCCESS)
            return status;
        all_disabled = 0u;
        (void)audio_ble_flash_control(STIM_DEVPWR, 0u, &all_disabled);
        status = g2_main_mspi_status_poll_480826(MAX_WAIT_US, PWRCTRL_AUDSSPWREN,
                                                 AUDSSPWRST_ALL_MASK, 0u, 1u);
        if (status != STATUS_SUCCESS)
            return status;
        all_disabled = 0u;
        (void)audio_ble_flash_control(STIM_AUDSSPWR, 0u, &all_disabled);
        break;

    default:
        status = STATUS_INVALID_ARG;
        break;
    }
    return status;
}
