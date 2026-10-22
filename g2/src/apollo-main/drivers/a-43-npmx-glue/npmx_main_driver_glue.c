/* Stock D:\01_workspace\s200_ap510b_iar_git\driver\npmx_driver_transplant\src\npmx_main_driver.c
 * (rows of that source not written in drivers/power/npm1300/npmx_main_driver.c):
 *   0x510fe2..0x511001 npmx interrupt service (first function of the unit),
 *   0x511b74..0x511bbf charge_status_inform_fuel_gauge (name from the caller's
 *                      log string "charge_status_inform_fuel_gauge=%d"),
 *   0x5128a0..0x5128f3 fuel-gauge poll.
 * Literal pool words used: 0x511948 (0x2bad0001), 0x512608 (0x20073b18),
 * 0x512a64 (1000.0f), 0x512b10 (0.2f), 0x512c30..0x512c3c.
 *
 * charge_status_inform follows the Nordic npm1300_fuel_gauge sample: the nPM1300
 * BCHGCHARGESTATUS bits map to nrf_fuel_gauge_charge_state (COMPLETE bit 1 -> 5,
 * TRICKLE bit 2 -> 1, CC bit 3 -> 2, CV bit 4 -> 4, else IDLE 0). The closed
 * nrf_fuel_gauge library is only called here, not reconstructed.
 *
 * Uses single-precision FP with the hard-float convention: profile g2-apollo-main-3. */
#include <stdint.h>
#include "g2_bq27427.h"

#define NPMX_ERROR_INVALID_PARAM 0x2bad0001u
/* npmx_instance_t.interrupt (layout in drivers/power/npmx-core/npmx_core.c). */
#define NPMX_INSTANCE_INTERRUPT_OFFSET 0xccu

/* nrf_fuel_gauge.h enum values. */
#define NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_STATE_CHANGE 2u
#define NRF_FUEL_GAUGE_CHARGE_STATE_IDLE     0u
#define NRF_FUEL_GAUGE_CHARGE_STATE_TRICKLE  1u
#define NRF_FUEL_GAUGE_CHARGE_STATE_CC       2u
#define NRF_FUEL_GAUGE_CHARGE_STATE_CV       4u
#define NRF_FUEL_GAUGE_CHARGE_STATE_COMPLETE 5u

/* nPM1300 BCHGCHARGESTATUS bits. */
#define NPM1300_CHG_STATUS_COMPLETE_MASK 0x02u
#define NPM1300_CHG_STATUS_TRICKLE_MASK  0x04u
#define NPM1300_CHG_STATUS_CC_MASK       0x08u
#define NPM1300_CHG_STATUS_CV_MASK       0x10u

#define FUEL_GAUGE_MIN_T_DELTA_S 0.2f

struct npmx_instance;

/* union nrf_fuel_gauge_ext_state_info_data: only charge_state is used here. */
typedef union {
    uint8_t charge_state; /* enum nrf_fuel_gauge_charge_state, 1 byte in stock */
    float value;
} nrf_fuel_gauge_ext_state_info_data_t;

extern void npmx_core_interrupt(struct npmx_instance *p_pm);
extern uint32_t npmx_core_proc(struct npmx_instance *p_pm);
extern int32_t nrf_fuel_gauge_ext_state_update_55f74c(uint32_t type, const void *info); /* closed library */
extern uint32_t osKernelGetTickCount(void); /* 0x4490cc */
extern __attribute__((pcs("aapcs-vfp"))) void process_fuel_gauge_51201c(float t_delta);

extern g2_charger_telemetry_t g2_charger_telemetry; /* RAM 0x20073b18 */
extern uint32_t g2_fuel_gauge_ref_time;             /* RAM 0x2007481c tick of the previous poll */
extern uint32_t g2_fuel_gauge_now_tick;             /* RAM 0x20074820 */
extern uint32_t g2_fuel_gauge_delta_ms;             /* RAM 0x20074824 */
extern float g2_fuel_gauge_t_delta;                 /* RAM 0x20074828 seconds */

/* Returns NPMX_ERROR_INVALID_PARAM while a previous interrupt is still pending,
 * otherwise flags it and processes the events at once. */
uint32_t npmx_interrupt_handler_510fe2(struct npmx_instance *p_pm)
{
    if (((const uint8_t *)p_pm)[NPMX_INSTANCE_INTERRUPT_OFFSET] != 0u)
        return NPMX_ERROR_INVALID_PARAM;
    npmx_core_interrupt(p_pm);
    return npmx_core_proc(p_pm);
}

int32_t charge_status_inform_fuel_gauge_511b74(uint8_t charger_status)
{
    nrf_fuel_gauge_ext_state_info_data_t state_info;

    if ((charger_status & NPM1300_CHG_STATUS_COMPLETE_MASK) != 0u)
        state_info.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_COMPLETE;
    else if ((charger_status & NPM1300_CHG_STATUS_TRICKLE_MASK) != 0u)
        state_info.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_TRICKLE;
    else if ((charger_status & NPM1300_CHG_STATUS_CC_MASK) != 0u)
        state_info.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_CC;
    else if ((charger_status & NPM1300_CHG_STATUS_CV_MASK) != 0u)
        state_info.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_CV;
    else
        state_info.charge_state = NRF_FUEL_GAUGE_CHARGE_STATE_IDLE;

    /* Product addition to the Nordic sample: publish the state in the
     * shared charger telemetry word. */
    g2_charger_telemetry.charge_status = state_info.charge_state;
    return nrf_fuel_gauge_ext_state_update_55f74c(NRF_FUEL_GAUGE_EXT_STATE_INFO_CHARGE_STATE_CHANGE, &state_info);
}

/* Device-manager poll (0x4c687a): run the fuel gauge once at least 200 ms
 * have passed since the previous poll (the reference tick always advances). */
void npmx_fuel_gauge_poll_5128a0(void)
{
    g2_fuel_gauge_now_tick = osKernelGetTickCount();
    g2_fuel_gauge_delta_ms = g2_fuel_gauge_now_tick - g2_fuel_gauge_ref_time;
    g2_fuel_gauge_ref_time = g2_fuel_gauge_now_tick;
    g2_fuel_gauge_t_delta = (float)g2_fuel_gauge_delta_ms / 1000.0f;
    if (g2_fuel_gauge_t_delta >= FUEL_GAUGE_MIN_T_DELTA_S)
        process_fuel_gauge_51201c(g2_fuel_gauge_t_delta);
}
