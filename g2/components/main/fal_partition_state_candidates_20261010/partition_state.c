/* FAL static two-row partition initialization and cache fill.
 * Product row definitions and flash-device discovery have separate owners. */
#include <stdint.h>

extern const uint8_t g2_fal_partition_rows[];
extern uint32_t g2_fal_flash_device_find(uint32_t flash_name);

uint32_t g2_fal_partition_table_base;
uint32_t g2_fal_partition_table_length;
uint32_t g2_fal_device_cache[2];
uint8_t g2_fal_partition_init_ok;

int32_t g2_fal_check_partition_cache(uint32_t table, uint32_t length)
{
    for (uint32_t i = 0; i < length; ++i) {
        const uint32_t row = table + i * 64u;
        const uint32_t device = g2_fal_flash_device_find(row + 0x1cu);
        if (device == 0u) continue;
        const int32_t offset = *(const int32_t *)(uintptr_t)(row + 0x34u);
        const int32_t device_length = *(const int32_t *)(uintptr_t)(device + 0x1cu);
        if (offset >= device_length) {
            g2_fal_partition_table_length = 0;
            return -1;
        }
        g2_fal_device_cache[i] = device;
    }
    return 0;
}

uint32_t g2_fal_partition_init(void)
{
    if (g2_fal_partition_init_ok) return g2_fal_partition_table_length;
    g2_fal_partition_table_base = (uint32_t)(uintptr_t)g2_fal_partition_rows;
    g2_fal_partition_table_length = 2u;
    if (g2_fal_check_partition_cache(g2_fal_partition_table_base, 2u) == 0)
        g2_fal_partition_init_ok = 1u;
    return g2_fal_partition_table_length;
}
