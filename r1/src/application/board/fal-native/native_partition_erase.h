/* Included at fal_partition_erase's definition in the pinned FAL unit. */
#ifndef R1_FAL_NATIVE_PARTITION_ERASE_H
#define R1_FAL_NATIVE_PARTITION_ERASE_H
#include <stddef.h>
extern int r1_native_printf(const char *, ...);
int fal_partition_erase(const struct fal_partition *part, uint32_t addr,
                       size_t size)
{
    _Static_assert(sizeof(size_t) == 4, "native size word");
    _Static_assert(offsetof(struct fal_partition, len) == 56 &&
                   offsetof(struct fal_partition, offset) == 52 &&
                   offsetof(struct fal_flash_dev, ops.erase) == 48,
                   "native partition/driver fields");
    if (part == NULL) {
        r1_native_printf("(%s) has assert failed at %s.\n", "part", __func__);
        for (;;) {}
    }
    uint32_t limit = ((const volatile struct fal_partition *)part)->len;
    if (addr > limit || (uint32_t)size > limit - addr) {
        r1_native_printf("\033[31;22m[E/FAL] (%s:%d) ", __func__, 494);
        r1_native_printf("Partition erase error! Partition address out of bound.");
        r1_native_printf("\033[0m\n");
        return -1;
    }
    const struct fal_flash_dev *flash = flash_device_find_by_part(part);
    if (flash == NULL) {
        r1_native_printf("\033[31;22m[E/FAL] (%s:%d) ", __func__, 501);
        r1_native_printf("Partition erase error! Don't found flash device(%s) of the partition(%s).",
                         part->flash_name, part->name);
        r1_native_printf("\033[0m\n");
        return -1;
    }
    uint32_t offset = (uint32_t)((const volatile struct fal_partition *)part)->offset;
    int (*erase)(long, size_t) =
        ((const volatile struct fal_flash_dev *)flash)->ops.erase;
    int result = erase((long)(offset + addr), size);
    if (result < 0) {
        r1_native_printf("\033[31;22m[E/FAL] (%s:%d) ", __func__, 508);
        r1_native_printf("Partition erase error! Flash device(%s) erase error!", part->flash_name);
        r1_native_printf("\033[0m\n");
    }
    return result;
}
#endif
