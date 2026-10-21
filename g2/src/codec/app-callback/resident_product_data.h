/* SPDX-License-Identifier: MIT
 * Typed image-A flash and module product data shared by native consumers.
 * Final SRAM/XIP placement and reset copy remain linker obligations.
 */
#ifndef GX8002_RESIDENT_PRODUCT_DATA_H
#define GX8002_RESIDENT_PRODUCT_DATA_H
#include <stdint.h>

struct gx8002_otp_config {
    uint32_t field0, field4, region_size, region_count, current_region;
};
struct gx8002_flash_protect_entry {
    uint8_t status_value, status_mask, status2_value, status2_mask;
    uint32_t protected_bytes;
};
struct gx8002_flash_catalog_entry {
    const char *name;
    uint32_t jedec, capacity, field12;
    volatile uint32_t *protection_map;
    volatile struct gx8002_otp_config *otp;
};
struct gx8002_module_config_data {
    uint8_t modes[4];
    uint32_t words[17];
};
struct gx8002_module_entry {
    uint32_t id;
    int8_t bit_primary, bit_secondary, dependency_bit;
    uint8_t field7;
    const uint32_t *config;
    const uint8_t *mode;
};
extern volatile uint32_t gx8002_flash_protection_maps_26ff8[6];
extern const struct gx8002_flash_protect_entry gx8002_otp_protect_2657c[5];
extern const struct gx8002_flash_protect_entry gx8002_otp_protect_265a4[7];
extern const struct gx8002_flash_protect_entry gx8002_otp_protect_265dc[9];
extern volatile struct gx8002_otp_config gx8002_flash_otp_config_266cc;
extern const struct gx8002_flash_catalog_entry gx8002_flash_catalog_26624[7];
extern const struct gx8002_module_config_data gx8002_module_config_26880;
extern const struct gx8002_module_entry gx8002_module_table_266e0[26];

#endif
