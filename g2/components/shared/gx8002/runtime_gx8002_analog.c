/* SPDX-License-Identifier: MIT */
/* Recovered GX8002 analog register leaves.
 * The NationalChip SDK headers identify the ABI; authenticated C-SKY bodies
 * establish masks, saturation, byte narrowing, and 32-bit MMIO accesses.
 * Do not normalize flag inputs: the original shifts them before narrowing.
 */
#include "runtime_gx8002_analog.h"

#if defined(OPEN_CFW_GX8002_ANALOG_HOST_TEST)
extern volatile uint32_t open_cfw_gx8002_analog_test_registers[6];
#define ANALOG_WORD(index) open_cfw_gx8002_analog_test_registers[index]
#else
#define ANALOG_WORD(index) (((volatile uint32_t *)0xA0005080U)[index])
#endif

int gx_analog_set_pga_itrim(uint32_t itrim)
{
    uint32_t previous = ANALOG_WORD(2);
    uint32_t limited = itrim < 63U ? itrim : 63U;
    ANALOG_WORD(2) = (uint8_t)((previous & 0xC0U) | limited);
    return 0;
}

int gx_analog_set_pga_bypass(uint32_t bypass)
{
    uint32_t previous = ANALOG_WORD(2);
    ANALOG_WORD(2) = (uint8_t)((previous & 0xBFU) | (bypass << 6));
    return 0;
}

int gx_analog_set_pga_enable(uint32_t enable)
{
    uint32_t previous = ANALOG_WORD(4);
    ANALOG_WORD(4) = (uint8_t)((previous & 0xBFU) | (enable << 6));
    return 0;
}

int gx_analog_set_adc_sample_clk_sel(uint32_t select)
{
    uint32_t previous = ANALOG_WORD(5);
    ANALOG_WORD(5) = (uint8_t)((previous & 0xFEU) | select);
    return 0;
}

int gx_analog_set_adc_out_at_clk(uint32_t clock)
{
    uint32_t previous = ANALOG_WORD(5);
    ANALOG_WORD(5) = (uint8_t)((previous & 0xFDU) | (clock << 1));
    return 0;
}

int gx_analog_set_adc_in_sel(uint32_t select)
{
    uint32_t previous = ANALOG_WORD(5);
    ANALOG_WORD(5) = (uint8_t)((previous & 0xFBU) | (select << 2));
    return 0;
}

int gx_analog_set_adc_rstn(uint32_t reset_n)
{
    uint32_t previous = ANALOG_WORD(5);
    ANALOG_WORD(5) = (uint8_t)((previous & 0xF7U) | (reset_n << 3));
    return 0;
}
