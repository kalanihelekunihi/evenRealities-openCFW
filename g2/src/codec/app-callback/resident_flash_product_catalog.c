/* SPDX-License-Identifier: MIT
 * Typed native image-A product data: six flash catalog entries, sentinel,
 * OTP configuration and XIP names. Source extents in the stock images are
 * 0x10026624..0x100266e0 and 0x1020be54..0x1020be89. Runtime placement
 * 0x20026624..0x200266e0 remains a linker/scatter-copy contract.
 */
#include "resident_product_data.h"
_Static_assert(sizeof(struct gx8002_otp_config) == 20,
               "native OTP config ABI");
_Static_assert(sizeof(struct gx8002_flash_catalog_entry) == 24,
               "native catalog entry ABI");

#define STOCK_NAME(sym, section_name, literal) \
    const char sym[] __attribute__((section(section_name), used, aligned(1))) = literal
STOCK_NAME(gx8002_flash_name_p25q21l, ".gx8002.flash_name.be54", "p25q21l");
/* Stock 0x1020BE5C (gx8002_flash_name_p25q40l, data) */
STOCK_NAME(gx8002_flash_name_p25q40l, ".gx8002.flash_name.be5c", "p25q40l");
/* Stock 0x1020BE64 (gx8002_flash_name_p25q80l, data) */
STOCK_NAME(gx8002_flash_name_p25q80l, ".gx8002.flash_name.be64", "p25q80l");
/* Stock 0x1020BE6C (gx8002_flash_name_en25s20a, data) */
STOCK_NAME(gx8002_flash_name_en25s20a, ".gx8002.flash_name.be6c", "en25s20a");
/* Stock 0x1020BE75 (gx8002_flash_name_en25s40a, data) */
STOCK_NAME(gx8002_flash_name_en25s40a, ".gx8002.flash_name.be75", "en25s40a");
/* Stock 0x1020BE7E (gx8002_flash_name_zb25wq80a, data) */
STOCK_NAME(gx8002_flash_name_zb25wq80a, ".gx8002.flash_name.be7e", "zb25wq80a");
#undef STOCK_NAME

volatile uint32_t gx8002_flash_protection_maps_26ff8[6]
    __attribute__((section(".bss.gx8002.flash_protection_maps.26ff8"), used,
                   aligned(4)));

/* Stock 0x100266CC (flash_otp_descriptor) */
volatile struct gx8002_otp_config gx8002_flash_otp_config_266cc
    __attribute__((section(".gx8002.flash_otp_config.266cc"), used,
                   aligned(4))) = {0x1000u, 0x1000u, 0x200u, 3u, 0u};

const struct gx8002_flash_catalog_entry gx8002_flash_catalog_26624[7]
    __attribute__((section(".gx8002.flash_catalog.26624"), used,
                   aligned(4))) = {
    {gx8002_flash_name_p25q21l, 0x854012u, 0x3f000u, 0x60u,
     gx8002_flash_protection_maps_26ff8, &gx8002_flash_otp_config_266cc},
    {gx8002_flash_name_p25q40l, 0x856013u, 0x7f000u, 0x60u,
     gx8002_flash_protection_maps_26ff8 + 2, &gx8002_flash_otp_config_266cc},
    {gx8002_flash_name_p25q80l, 0x856014u, 0xff000u, 0x60u,
     gx8002_flash_protection_maps_26ff8 + 4, &gx8002_flash_otp_config_266cc},
    {gx8002_flash_name_en25s20a, 0x1c3812u, 0x3f000u, 0x60u, 0, 0},
    {gx8002_flash_name_en25s40a, 0x1c3813u, 0x7f000u, 0x60u, 0, 0},
    {gx8002_flash_name_zb25wq80a, 0x5e3414u, 0xff000u, 0x60u,
     gx8002_flash_protection_maps_26ff8 + 4, &gx8002_flash_otp_config_266cc},
    {0, 0, 0, 0, 0, 0},
};
