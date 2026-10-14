/* FAL flash-device name lookup; product table and count are separate data. */
#include <stdint.h>
#include "../fal_product_config_candidates_20261013/product_tables.h"


static int name_equal_24(uint32_t a, uint32_t b)
{
    const uint8_t *left = (const uint8_t *)(uintptr_t)a;
    const uint8_t *right = (const uint8_t *)(uintptr_t)b;
    for (uint32_t i = 0; i < 24u; ++i) {
        const uint8_t x = left[i], y = right[i];
        if (x != y) return 0;
        if (x == 0u) return 1;
    }
    return 1;
}

uint32_t g2_fal_flash_device_find(uint32_t name)
{
    for (uint32_t i = 0; i < g2_fal_flash_device_count; ++i) {
        const uint32_t device = (uint32_t)(uintptr_t)g2_fal_flash_device_table[i];
        if (name_equal_24(name, device)) return device;
    }
    return 0u;
}
