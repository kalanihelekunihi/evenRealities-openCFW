/* SPDX-License-Identifier: MIT
 * Image-B 0x100035c0. Native CFG and parameter table match the pinned Grus
 * clk_priv.h _clk_set_module implementation (NationalChip 8bf9ee5c).
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

int32_t gx8002_image_b_clock_module_select_100035c0(uint32_t module,
                                                       uint32_t source)
{
    return _clk_set_module((GX_CLOCK_MODULE)module,
                           (GX_CLOCK_MODULE_SOURCE)source);
}

/* The native 0x100034e0 provider uses the same parameter table. Keeping both
 * wrappers in one translation unit preserves that table's single ownership. */
int32_t gx8002_image_b_clock_module_info_100034e0(
    uint32_t module, GX_CLOCK_MODULE_INFO *info)
{
    return __module_get_info((GX_CLOCK_MODULE)module, info);
}

/* Native 0x10003788 and 0x100038e8 follow these pinned inline SDK bodies,
 * including descriptor lookup, gate ordering, divider pulses, and DTO writes.
 * Keeping them in this TU shares the one private module/parameter table. */
void gx8002_image_b_clock_config_10003788(uint32_t module, uint32_t divider)
{
    _clk_set_div((GX_CLOCK_MODULE)module, (uint16_t)divider);
}

void gx8002_image_b_clock_config_flags_100038e8(uint32_t module,
                                                  uint32_t dto,
                                                  uint32_t enable)
{
    _clk_set_dto((GX_CLOCK_MODULE)module, dto, (int)enable);
}

