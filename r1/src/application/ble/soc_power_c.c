/* Direct nRF52840 REG1 DC/DC control for a C-built SoftDevice port.
 * The stock-compatible build continues to use the Nordic SVC gateway. */
#include "nrf_soc.h"
#include "nrf_power.h"
#include "nrf_error.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
_Static_assert(NRF_POWER_DCDC_DISABLE == 0 && NRF_POWER_DCDC_ENABLE == 1,
               "Nordic DC/DC mode values");

uint32_t sd_power_dcdc_mode_set(uint8_t mode)
{
    if (mode > NRF_POWER_DCDC_ENABLE) return NRF_ERROR_INVALID_PARAM;
    nrf_power_dcdcen_set(mode == NRF_POWER_DCDC_ENABLE);
    return NRF_SUCCESS;
}

static uint32_t gpregret_change(uint32_t id, uint32_t bits, uint8_t set)
{
    if (id > 1u) return NRF_ERROR_INVALID_PARAM;
    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    uint8_t value = id == 0u ? nrf_power_gpregret_get()
                             : nrf_power_gpregret2_get();
    value = set ? (uint8_t)(value | (uint8_t)bits)
                : (uint8_t)(value & (uint8_t)~bits);
    if (id == 0u) nrf_power_gpregret_set(value);
    else nrf_power_gpregret2_set(value);
    __set_PRIMASK(interrupt_mask);
    return NRF_SUCCESS;
}

uint32_t sd_power_gpregret_set(uint32_t id, uint32_t bits)
{
    return gpregret_change(id, bits, 1u);
}

uint32_t sd_power_gpregret_clr(uint32_t id, uint32_t bits)
{
    return gpregret_change(id, bits, 0u);
}

uint32_t sd_power_system_off(void)
{
    nrf_power_system_off();
    return NRF_ERROR_SOC_POWER_OFF_SHOULD_NOT_RETURN;
}
#endif
