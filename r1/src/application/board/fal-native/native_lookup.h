/* Included at the pinned FAL helper definition, after its private state. */
#ifndef R1_FAL_NATIVE_LOOKUP_H
#define R1_FAL_NATIVE_LOOKUP_H
/* R1 64f74: use the existing FAL-owned table/cache, preserving raw bounds. */
extern int r1_native_printf(const char *, ...);
__attribute__((noinline)) static const struct fal_flash_dev *flash_device_find_by_part(const struct fal_partition *part)
{
    _Static_assert(sizeof(struct fal_partition) == 64, "native FAL partition stride");
    _Static_assert(sizeof(part_flash_cache[0]) == 4, "native cache pointer stride");
    uintptr_t address = (uintptr_t)part;
    uintptr_t base = (uintptr_t)*(const struct fal_partition *volatile *)&partition_table;
    if (address < base) {
        r1_native_printf("(%s) has assert failed at %s.\n", "part >= partition_table", __func__);
        for (;;) {}
    }
    uint32_t count = *(volatile size_t *)&partition_table_len;
    uintptr_t upper = base + (count << 6) - 64u;
    if (address > upper) {
        r1_native_printf("(%s) has assert failed at %s.\n", "part <= &partition_table[partition_table_len - 1]", __func__);
        for (;;) {}
    }
    int32_t difference = (int32_t)(address - base);
    return ((volatile struct part_flash_info *)part_flash_cache)[difference >> 6].flash_dev;
}
extern __typeof__(flash_device_find_by_part) r1_fal_native_device_by_partition
    __attribute__((alias("flash_device_find_by_part")));

#endif
