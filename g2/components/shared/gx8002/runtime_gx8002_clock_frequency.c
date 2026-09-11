/* SPDX-License-Identifier: MIT */
/* Adapter to authenticated NationalChip GRUS clock-frequency source. */
#include <stddef.h>
#include <stdint.h>
#include "clk_priv_frequency.h"
unsigned int open_cfw_gx8002_clock_frequency(unsigned int module)
{
    return _clk_get_module_frequence((GX_CLOCK_MODULE)module);
}

/* Public lookup contract prevents single-caller specialization of NULL handling. */
int open_cfw_gx8002_frequency_lookup(unsigned int module, GX_CLOCK_MODULE_INFO *info)
{
    return __module_get_info((GX_CLOCK_MODULE)module, info);
}

