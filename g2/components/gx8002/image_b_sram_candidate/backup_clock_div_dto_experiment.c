/* Stock image-B 0x10003788 divider and 0x100038e8 DTO setter.
 * The native descriptor lookup, gate disable/re-enable, divider pulse, and
 * DTO write sequence are attributable to pinned NationalChip Grus
 * arch/soc/grus/include/clk_priv.h at commit 8bf9ee5c. These wrappers
 * retain the SDK's complete C bodies; board tables remain separately owned.
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
