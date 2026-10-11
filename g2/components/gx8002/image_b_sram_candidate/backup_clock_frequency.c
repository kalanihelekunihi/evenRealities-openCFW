/* SPDX-License-Identifier: MIT
 * Image-B 0x10003cf0 from pinned NationalChip Grus clk_priv.h source.
 * The SDK owns the module parameter table and clock selection logic.
 */
#include <stdint.h>
#include <stddef.h>
#include <driver/gx_clock/gx_clock_v2.h>
#define __GX_CLOCK_H__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wincompatible-pointer-types"
#include <clk_priv.h>
#pragma GCC diagnostic pop

uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t module)
{
    return _clk_get_module_frequence((GX_CLOCK_MODULE)module);
}
