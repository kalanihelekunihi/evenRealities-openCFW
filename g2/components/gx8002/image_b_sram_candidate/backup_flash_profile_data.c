/* SPDX-License-Identifier: MIT
 * Typed image-B flash protection and JEDEC profile configuration.
 * Source: stage-2 payload offsets 0x13dfc..0x13f34 under the candidate
 * DRAM load mapping 0x20003000. Final runtime placement is not qualified.
 */
#include <stdint.h>

struct gx8002_image_b_protection_level {
    uint8_t set_status_05;
    uint8_t clear_status_05;
    uint8_t set_status_35;
    uint8_t clear_status_35;
    uint32_t protected_bytes;
};

struct gx8002_image_b_flash_profile {
    const char *name;
    uint32_t jedec_id;
    uint32_t address_limit;
    uint32_t configuration_word;
    uint32_t protection_binding_address;
    uint32_t sector_size_address;
};

_Static_assert(sizeof(struct gx8002_image_b_protection_level) == 8u,
               "native protection level stride");
_Static_assert(sizeof(struct gx8002_image_b_flash_profile) == 24u,
               "native flash profile stride");

const struct gx8002_image_b_protection_level
gx8002_image_b_protection_p25q21l[5] = {
    {0x00, 0x9c, 0x00, 0x41, 0x00000},
    {0x24, 0xfc, 0x00, 0x41, 0x10000},
    {0x28, 0xfc, 0x00, 0x41, 0x20000},
    {0x04, 0xfc, 0x40, 0x41, 0x30000},
    {0x1c, 0xfc, 0x00, 0x41, 0x40000},
};

const struct gx8002_image_b_protection_level
gx8002_image_b_protection_p25q40l[7] = {
    {0x00, 0x9c, 0x00, 0x41, 0x00000},
    {0x24, 0xfc, 0x00, 0x41, 0x10000},
    {0x28, 0xfc, 0x00, 0x41, 0x20000},
    {0x2c, 0xfc, 0x00, 0x41, 0x40000},
    {0x08, 0xfc, 0x40, 0x41, 0x60000},
    {0x04, 0xfc, 0x40, 0x41, 0x70000},
    {0x1c, 0xfc, 0x00, 0x41, 0x80000},
};

const struct gx8002_image_b_protection_level
gx8002_image_b_protection_p25q80l[9] = {
    {0x00, 0x9c, 0x00, 0x41, 0x000000},
    {0x24, 0xfc, 0x00, 0x41, 0x010000},
    {0x28, 0xfc, 0x00, 0x41, 0x020000},
    {0x2c, 0xfc, 0x00, 0x41, 0x040000},
    {0x30, 0xfc, 0x00, 0x41, 0x080000},
    {0x0c, 0xfc, 0x40, 0x41, 0x0c0000},
    {0x08, 0xfc, 0x40, 0x41, 0x0e0000},
    {0x04, 0xfc, 0x40, 0x41, 0x0f0000},
    {0x1c, 0xfc, 0x00, 0x41, 0x100000},
};

/* The protection binding addresses are writable SRAM slots populated by
 * 0x10007f80. Names and profile fields are authenticated payload values. */
const struct gx8002_image_b_flash_profile gx8002_image_b_flash_profiles[7] = {
    {"p25q21l", 0x00854012, 0x0003f000, 0x60, 0x20017644, 0x20016f4c},
    {"p25q40l", 0x00856013, 0x0007f000, 0x60, 0x2001764c, 0x20016f4c},
    {"p25q80l", 0x00856014, 0x000ff000, 0x60, 0x20017654, 0x20016f4c},
    {"en25s20a", 0x001c3812, 0x0003f000, 0x60, 0, 0},
    {"en25s40a", 0x001c3813, 0x0007f000, 0x60, 0, 0},
    {"zb25wq80a", 0x005e3414, 0x000ff000, 0x60, 0x20017654, 0x20016f4c},
    {0, 0, 0, 0, 0, 0},
};

const uint32_t gx8002_image_b_flash_erase_sector_bytes = 0x1000u;
