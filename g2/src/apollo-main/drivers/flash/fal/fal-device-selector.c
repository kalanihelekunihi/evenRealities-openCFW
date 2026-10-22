/* Stock FAL partition-cache selector. RAM objects are separate source owners.
 * Callers must provide a pointer into the initialized two-row partition table. */
#include <stdint.h>

extern uint32_t g2_fal_partition_table_base;
extern uint32_t g2_fal_device_cache[];

/* Stock 0x597D10 (fal flash_device_find_by_part) */
uint32_t g2_fal_device_for_partition(uint32_t partition)
{
    const uint32_t base = g2_fal_partition_table_base;
    const int32_t index = (int32_t)(partition - base) >> 6;
    return g2_fal_device_cache[index];
}
