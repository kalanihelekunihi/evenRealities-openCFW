/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10024730, gx_analog_set_ldo_dig_voltage (same body as
 * NationalChip lvp_kws 8bf9ee5c drivers_lib/analog/ldo.o). It fills the
 * digital-LDO control word and passes it to gx_pmu_ctrl_set (here
 * 0x10025d74, selector 8), which stores the whole 32-bit word to
 * 0xa0000038.
 *
 * Deliberate change: the stock body builds that word in an uninitialised
 * stack slot, setting only bits 3:0 (voltage) and bit 4 (enable), so bits
 * 31:5 written to 0xa0000038 were stale stack contents. Here the word starts
 * at 0. The stock getter (gx_analog_get_ldo_dig_voltage) reads back only
 * bits 4:0, so 0 is the only value the driver itself defines for the rest.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_platform_config_25d74(uint32_t module,
                                                      uint32_t *input);

/* Stock 0x10024730 (gx8002_digital_voltage) */
int32_t gx8002_resident_digital_voltage_24730(int32_t voltage)
{
    if (voltage == -1)                        /* LDO_DIG_VOLTAGE_INVALID */
        return -1;
    uint32_t control = 0;
    control |= (uint32_t)voltage & 0xfu;      /* bits 3:0 voltage */
    control |= UINT32_C(1) << 4;              /* bit 4 enable */
    (void)gx8002_resident_platform_config_25d74(8u, &control);
    return 0;
}
